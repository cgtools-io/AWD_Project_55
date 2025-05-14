from flask import Blueprint, request, jsonify, url_for, render_template, flash, redirect, session, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFError
import logging
from urllib.parse import urlparse
import os
import pandas as pd
import csv
import re

import app.constants as msg
from app.extensions import db
from app.forms.user_forms import SignupForm, LoginForm
from app.models import User, Admin, Summary
from app.forms.file_upload_form import FileUploadForm
from werkzeug.utils import secure_filename

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

@user.route('/signup', methods=['GET', 'POST'])
def signup():
    logging.debug("User signup endpoint accessed")

    form = SignupForm()

    if request.method == 'POST':
        if form.validate_on_submit():
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

@user.route('/login', methods=['GET', 'POST'])
def login():
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
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Error in {field}: {error}', 'danger')
                        logger.error(f'Error in {field}: {error}')

        except CSRFError:
            flash(msg.CSRF_FAILED)
            logger.error('CSRF token validation failed')

    return render_template('auth/login.html', form=form)

@user.route('/logout')
@login_required
def logout():
    logging.debug("User logout endpoint accessed")

    if current_user.is_authenticated:
        logout_user()
        flash(msg.LOGOUT_SUCCESS, 'success')
    else:
        flash(msg.NOT_LOGGED_IN)

    return redirect(url_for('index'))

@user.route('/file_upload', methods=['GET', 'POST'])
@login_required
def file_upload():

    form = FileUploadForm()
    form_state = request.args.get('form_state', 1)

    if request.method == 'POST':

        print(request.form)

        filename = None

        if form.validate_on_submit():
            file = form.file.data
            if isinstance(file, list):
                file = file[0]

            filename = secure_filename(file.filename)
            upload_folder = os.path.join('app/static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            flash(msg.UPLOAD_SUCCESS, 'success')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')

        return render_template('user/file_upload.html', filename=filename, form_state=2, form=form, old_form=request.form)

    return render_template('user/file_upload.html', form=form, form_state=form_state, old_form=None)

@user.route('/visual')
@login_required
def visual():
    return render_template('user/visual.html')    

@user.route('/share')
@login_required
def share():
    return render_template('user/share_data.html')

@user.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash(msg.CSRF_FAILED, 'danger')
    return redirect(request.url or url_for('index'))

@user.route("/file_upload/process/<filename>", methods=["POST"])
@user.route("/file_upload/process/", methods=["POST"])
@login_required


def process_csv(filename=None):
    from datetime import datetime

    if filename is None:
        flash("No file uploaded.", "danger")
        logging.error("No file uploaded.")
        return redirect(url_for('user.file_upload', form_state=2))

    file_path = os.path.join('app/static/uploads', filename)

    if not os.path.exists(file_path):
        flash("File not found.", "danger")
        return redirect(url_for('user.file_upload'))

    current_app.logger.debug("make sure file is reached")
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        current_app.logger.debug("Rows reached")

        for row in reader:
            logger.debug(f"Processing row: {row.get('Value $')}")
            if row.get('Value $') == '-':
                continue
            if row.get('Type') == 'Buy':
                total_buy_val += float(row.get('Value $', 0).replace(',', ''))
            elif row.get('Type') == 'Sell':
                total_sell_val += float(row.get('Value $', 0).replace(',', ''))
    
    flash("CSV file processed successfully!", "success")
    flash(f"Total Buy Value: {total_buy_val} Total Sell Value: {total_sell_val}", "info")
    logging.debug(f"Total Buy Value: {total_buy_val} Total Sell Value: {total_sell_val}")

    print(f"Saving summary for user {current_user.id} – Buy: {total_buy_val}, Sell: {total_sell_val}") # debug print

    # Save the summary to the database
    summary = Summary(
        user_id=current_user.id,
        total_buy=total_buy_val,
        total_sell=total_sell_val
    )
    db.session.add(summary)
    db.session.commit()
    return redirect(url_for('user.dashboard'))

@user.route('/dashboard')
@login_required
def dashboard():
    # Get the latest summary for the logged-in user
    summary = db.session.execute(
        db.select(Summary)
        .where(Summary.user_id == current_user.id)
        .order_by(Summary.id.desc())
    ).scalars().first()

    total_buy_val = summary.total_buy if summary else 0
    total_sell_val = summary.total_sell if summary else 0

    return render_template(
        'user/dashboard.html',
        total_buy_val=total_buy_val,
        total_sell_val=total_sell_val
    )