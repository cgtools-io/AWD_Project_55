from flask import Blueprint, request, jsonify, url_for, render_template, flash, redirect, session, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFError
import logging
from urllib.parse import urlparse
import os
import pandas as pd
from datetime import datetime
import csv
import re
from werkzeug.utils import secure_filename
import json

import app.constants as msg
from app.extensions import db
from app.forms.user_forms import SignupForm, LoginForm
from app.models import User, Admin, Summary, SharedSummary
from app.forms.file_upload_form import FileUploadForm
from app.forms.share_form import ShareForm
from werkzeug.utils import secure_filename
from app.utils.cgt_processing import parse_binance_csv, calculate_cgt_binance
from app.utils.portfolio_pnl import calculate_pnl_stats


def clean_float(value):
    try:
        # Remove all non-digit, non-dot, and non-minus characters
        cleaned = re.sub(r'[^0-9.\-]', '', str(value))
        return float(cleaned)
    except:
        return 0.0


user = Blueprint('user', __name__)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME') 
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD') 

logger = logging.getLogger(__name__)

@user.route('/signup/', methods=['GET', 'POST'])
def signup():
    # Render and process the user signup form.
    logging.debug("User signup endpoint accessed")

    form = SignupForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Create and store new user
            new_user = User(
                username=form.username.data,
                email=form.email.data
            )

            logging.debug(f"Creating user: {new_user.username}, {new_user.email}")
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()

            logging.debug("New user successfully committed to the database.")
            flash(msg.ACCOUNT_CREATED, 'success')
            return redirect(url_for('user.login'))
        
        # Form was invalid — display detailed errors
        field_names = {
            'username': 'Username',
            'email': 'Email address',
            'password': 'Password',
            'confirm_password': 'Password confirmation',
        }

        for field, errors in form.errors.items():
            for error in errors:
                readable_field = field_names.get(field, field)
                logging.error(f'Error in {readable_field}: {error}')
                
    return render_template('auth/signup.html', form=form)

@user.route('/login/', methods=['GET', 'POST'])
def login():
    # Handle login logic for users and admins.
    logging.debug("User login endpoint accessed")

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'POST':
        try:
            # Returns true if form validators pass after submission
            if form.validate_on_submit():
                # Query the database for the user with the given username
                user = db.session.execute(
                    db.select(User).where(User.username == form.username.data)
                ).scalar()

                if form.username.data == ADMIN_USERNAME and form.password.data == ADMIN_PASSWORD:
                    # Check if logging in as admin
                    admin = Admin(0, ADMIN_USERNAME)
                    login_user(admin, remember=form.remember.data)
                    logger.debug(f'Admin {admin.username} logged in successfully')
                    logger.debug(f'Admin authenticated: {admin.is_authenticated}')
                    logger.debug(f'Stuff: {current_user.is_authenticated}, {current_user.username}, {current_user.id}')
                    return redirect(url_for('index'))

                # Check if the user exists and if the password is correct
                if not user or not user.check_password(form.password.data):
                    flash(msg.INVALID_CREDENTIALS, 'danger')
                    return redirect(url_for('user.login'))
                
                login_user(user, remember=form.remember.data)
                flash(msg.LOGIN_SUCCESS, 'success')
                logger.debug(f'User {user.username} logged in successfully')

                # Redirect to the next page (default: index page)
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                # Form validation failed
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Error in {field}: {error}', 'danger')
                        logger.error(f'Error in {field}: {error}')

        except CSRFError:
            flash(msg.CSRF_FAILED)
            logger.error('CSRF token validation failed')

    return render_template('auth/login.html', form=form)

@user.route('/logout/')
@login_required
def logout():
    logging.debug("User logout endpoint accessed")

    # If user is logged in, perform logout and flash success
    if current_user.is_authenticated:
        logout_user()
        flash(msg.LOGOUT_SUCCESS, 'success')
    else:
        # Shouldn't hit this due to @login_required, but here as fallback
        flash(msg.NOT_LOGGED_IN)

    # Redirect user to home page after logout
    return redirect(url_for('index'))

@user.route('/file_upload/', methods=['GET', 'POST'])
@user.route('/file_upload/<filename>', methods=['GET', 'POST'])
@login_required
def file_upload(filename=None):
    # Load file upload form
    form = FileUploadForm()

    if request.method == 'POST':
        # Save broker selection in session to prefill next time
        session['last_selected_broker'] = form.broker.data
        session.modified = True

        # If form passed validation (e.g., file selected, allowed type)
        if form.validate_on_submit():

            file = form.file.data
            if isinstance(file, list):
                file = file[0]

            # Secure filename and save file to server
            filename = secure_filename(file.filename)
            upload_folder = os.path.join('app/static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Flash success and store filename in session
            flash(msg.UPLOAD_SUCCESS, 'success')
            session['last_uploaded_file'] = filename
            session.modified = True

            total_cgt = None

            # Binance CSV parsing
            if request.form['broker'] == 'binance':

                if not os.path.exists(file_path):
                    flash(msg.NO_FILE, "danger")

                # Parse uploaded Binance CSV into DataFrame
                df = parse_binance_csv(filename)
                if isinstance(df, str):
                    flash(f"{df}", "danger")
                else:
                    # Calculate CGT + portfolio stats
                    total_cgt = calculate_cgt_binance(df)
                    total_cost, total_mv, pnl_graph = calculate_pnl_stats(df)
                    print(json.dumps(pnl_graph))

            elif request.form['broker'] == 'kraken':
                # TODO: Implement Kraken CSV parsing
                flash("Does nothing yet", "danger")
                pass

            logging.debug(f"Total CGT: {total_cgt}")

            # If CGT calculated successfully, save summary to DB
            if total_cgt is not None:

                new_summary = Summary(
                    user_id=current_user.id,
                    filename=filename,
                    total_cgt=total_cgt,
                    total_cost=total_cost,
                    total_mv=total_mv,
                    pnl_graph=json.dumps(pnl_graph)
                )

                db.session.add(new_summary)
                db.session.commit()

                logging.debug(f"New summary created: {new_summary.filename}, {new_summary.total_cgt}")

        else:
            # Handle and display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')
        # Render page with form in "after upload" state
        return render_template('user/file_upload.html', form=form, form_state=2)
    # Render page with form in default state
    return render_template('user/file_upload.html', form=form, form_state=1)

@user.route('/visual/')
@login_required
def visual():
    # Fetch all summaries owned by the current user, newest first
    owned = db.session.execute(
        db.select(Summary).where(Summary.user_id == current_user.id).order_by(Summary.created_at.desc())
    ).scalars()

    # Get IDs of summaries that have been shared *with* this user
    shared_ids = db.session.execute(
        db.select(SharedSummary.summary_id).where(SharedSummary.to_user_id == current_user.id).order_by(SharedSummary.timestamp.desc())
    ).scalars().all()
    print(shared_ids)

    # Look up those shared summaries by ID
    shared = db.session.execute(
        db.select(Summary).where(Summary.id.in_(shared_ids)).order_by(Summary.created_at.desc())
    ).scalars()
    print(shared)
    
    # Render visualisation page with both owned and shared summaries
    return render_template('user/visual.html', owned=owned, shared=shared)    



@user.route('/get_summary/', methods=['POST']) 
@login_required
def get_summary():
    # Retrieve the summary ID sent from the frontend
    summary_id = request.json.get('summary_id')
    # Fetch the matching summary from the database
    summary = db.session.execute(
        db.select(Summary).where(Summary.id == summary_id)
    ).scalar()
    # Handle missing or unselected summaries gracefully
    if not summary and summary_id != "select":
        return jsonify({'error': 'Summary not found'}), 404
    elif not summary and summary_id == "select":
        return jsonify({'error': 'No file selected'}), 404
    # Return summary data as JSON
    return jsonify({
        'id': summary.id,
        'total_cgt': summary.total_cgt,
        'total_cost': summary.total_cost,
        'total_mv': summary.total_mv,
        'pnl_graph': summary.pnl_graph,
        'filename': summary.filename,
    })

@user.route('/share/', methods=['GET', 'POST'])
@login_required
def share():
    form = ShareForm()

    # Step 1: Only show summaries owned by current user
    my_summaries = Summary.query.filter_by(user_id=current_user.id).all()

    # Step 2: List all other users (to share with)
    other_users = User.query.filter(User.id != current_user.id).all()

    form.summary_id.choices   = [(s.id, f"{s.filename}, uploaded on: {s.created_at.strftime('%Y-%m-%d')}") for s in my_summaries]
    form.recipient_id.choices = [(u.id, u.username)         for u in other_users]

    # Populate dropdowns in the form
    if form.validate_on_submit():
        
        # Prevent duplicate shares
        exists = SharedSummary.query.filter_by(
            summary_id   = form.summary_id.data,
            from_user_id = current_user.id,
            to_user_id   = form.recipient_id.data
        ).first()

        if exists:
            flash("You've already shared this summary with that user.", "warning")
            return redirect(url_for('user.share'))
        # Create a new SharedSummary entry
        share = SharedSummary(
            summary_id   = form.summary_id.data,
            from_user_id = current_user.id,
            to_user_id   = form.recipient_id.data
        )
        db.session.add(share)
        db.session.commit()
        flash("Summary successfully shared!", "success")
        return redirect(url_for('user.share'))

    # Step 4: Load share history for display
    shared_by_me   = SharedSummary.query.filter_by(from_user_id=current_user.id).all()
    shared_with_me = SharedSummary.query.filter_by(to_user_id=current_user.id).all()

    return render_template(
        'user/share_data.html',
        form            = form,
        shared_by_me    = shared_by_me,
        shared_with_me  = shared_with_me
    )

@user.errorhandler(CSRFError)
def handle_csrf_error(e):
    # Handle CSRF failures gracefully
    flash(msg.CSRF_FAILED, 'danger')
    return redirect(request.url or url_for('index'))
