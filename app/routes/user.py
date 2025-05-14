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
from app.forms.share_form import ShareForm
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

    if request.method == 'POST':

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

        return redirect(url_for('user.file_upload', filename=filename))

    return render_template('user/file_upload.html', form=form)

@user.route('/visual')
@login_required
def visual():
    return render_template('user/visual.html')    

@user.route('/share', methods=['GET'])
@login_required
def share():
    form = ShareForm()
    # TODO: adjust the format, broke it down to help me with SQLAlchemy
    # Quesy the DB for all Summaries *current user* owns
    summaries = (
        Summary
        .query
        .filter(User.id= current_user.id)
        .all()
    )

    # Then query the dB for *other* users that might share with
    users = (
        User
        .query
        .filter(User.id! =current_user.id)
        .all()
    )

    #    Turn those two Python lists into the dropdown choices
    #    Each choice is a (value, label) tuple
    form.summary_id.choices   = [(s.id, f"Summary #{s.id}") for s in summaries]
    form.recipient_id.choices = [(u.id, u.username) for u in users]

    # Return the template, passing the form + any existing shared records
    return render_template('user/share_data.html', form=form)

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
        return redirect(url_for('user.file_upload'))

    file_path = os.path.join('app/static/uploads', filename)

    if not os.path.exists(file_path):
        flash("File not found.", "danger")
        return redirect(url_for('user.file_upload'))

    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        df['datetime'] = pd.to_datetime(df['Date(UTC)'], utc=True)
        df = df.rename(columns={
            'Side': 'Side',
            'Price': 'Price',
            'Executed': 'executed_amount',
            'Fee': 'fee_amount',
            'Pair': 'base_asset'
        })

        df['fee_amount'] = df['fee_amount'].apply(clean_float)
        df['executed_amount'] = df['executed_amount'].apply(clean_float)
        df['Price'] = df['Price'].apply(clean_float)



        df = df.sort_values(by='datetime')
        buy_pool = []
        cgt_results = []

        for _, row in df.iterrows():
            if row['Side'] == 'BUY':
                buy_pool.append({
                    'datetime': row['datetime'],
                    'asset': row['base_asset'],
                    'amount': clean_float(row['executed_amount']),
                    'price': clean_float(row['Price']),
                    'fee': clean_float(row['fee_amount'])
                })

            elif row['Side'] == 'SELL':
                sell_asset = row['base_asset']
                sell_amount = clean_float(row['executed_amount'])
                sell_price = clean_float(row['Price'])
                fee_amount = clean_float(row['fee_amount'])
                sale_proceeds = sell_amount * sell_price - fee_amount
                cost_base = 0.0

                while sell_amount > 0 and buy_pool:
                    earliest = buy_pool[0]
                    if earliest['asset'] != sell_asset:
                        buy_pool.pop(0)
                        continue

                    used = min(sell_amount, earliest['amount'])
                    cost = used * earliest['price']
                    cost_base += cost

                    earliest['amount'] -= used
                    if earliest['amount'] <= 0:
                        buy_pool.pop(0)

                    sell_amount -= used

                capital_gain = sale_proceeds - cost_base
                cgt_results.append(capital_gain)

        total_cgt = round(sum(cgt_results), 2)
        flash("CSV file processed successfully!")
        flash(f"Total CGT: ${total_cgt}", "info")
        return redirect(url_for('dashboard'))

    except Exception as e:
        logging.exception(f"Error processing CSV: {e}")
        flash("Failed to process CSV. Check format or logs.", "danger")
        return redirect(url_for('user.file_upload'))
