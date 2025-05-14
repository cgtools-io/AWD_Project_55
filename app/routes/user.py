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

import app.constants as msg
from app.extensions import db
from app.forms.user_forms import SignupForm, LoginForm
from app.models import User, Admin, Summary
from app.forms.file_upload_form import FileUploadForm
from app.utils.cgt_processing import parse_binance_csv, calculate_cgt_binance

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

@user.route('/file_upload/', methods=['GET', 'POST'])
@user.route('/file_upload/<filename>', methods=['GET', 'POST'])
@login_required
def file_upload(filename=None):

    print(request)
    print(request.form)

    form = FileUploadForm()

    if request.method == 'POST':

        session['last_selected_broker'] = form.broker.data
        session.modified = True

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
            session['last_uploaded_file'] = filename
            session.modified = True

            if not os.path.exists(file_path):
                flash(msg.NO_FILE, "danger")

            df = parse_binance_csv(filename)
            if isinstance(df, str):
                flash(f"{df}", "danger")

            total_cgt = calculate_cgt_binance(df)
            flash(f"Total CGT: ${total_cgt}", "info")

            new_summary = Summary(
                user_id=current_user.id,
                filename=filename,
                total_cgt=total_cgt,
            )

            db.session.add(new_summary)
            db.session.commit()

            logging.debug(f"New summary created: {new_summary.filename}, {new_summary.total_cgt}")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'danger')
        
        return render_template('user/file_upload.html', form=form, form_state=2)
    
    return render_template('user/file_upload.html', form=form, form_state=1)

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