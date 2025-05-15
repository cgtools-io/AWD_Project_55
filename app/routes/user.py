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
from app.models import User, Admin, Summary, SharedSummary
from app.forms.file_upload_form import FileUploadForm
from app.forms.share_form import ShareForm
from werkzeug.utils import secure_filename
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

            total_cgt = None

            if request.form['broker'] == 'binance':

                if not os.path.exists(file_path):
                    flash(msg.NO_FILE, "danger")

                df = parse_binance_csv(filename)
                if isinstance(df, str):
                    flash(f"{df}", "danger")
                else:
                    total_cgt = calculate_cgt_binance(df)
                    flash(f"Total CGT: ${total_cgt}", "info")

            elif request.form['broker'] == 'kraken':
                # TODO: Implement Kraken CSV parsing
                flash("Does nothing yet", "danger")
                pass

            logging.debug(f"Total CGT: {total_cgt}")

            if total_cgt is not None:

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

    options = db.session.execute(
        db.select(Summary).where(Summary.user_id == current_user.id).order_by(Summary.created_at.desc())
    ).scalars()
    return render_template('user/visual.html', options=options)    

@user.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    form = ShareForm()

    # 1) only pull summaries that *I* own
    my_summaries = Summary.query.filter_by(user_id=current_user.id).all()

    # 2) all other users
    other_users = User.query.filter(User.id != current_user.id).all()

    form.summary_id.choices   = [(s.id, f"#{s.id}: {s.filename}") for s in my_summaries]
    form.recipient_id.choices = [(u.id, u.username)         for u in other_users]

    if form.validate_on_submit():
        
        # 3) duplicate‐share guard
        exists = SharedSummary.query.filter_by(
            summary_id   = form.summary_id.data,
            from_user_id = current_user.id,
            to_user_id   = form.recipient_id.data
        ).first()

        if exists:
            flash("You've already shared this summary with that user.", "warning")
            return redirect(url_for('user.share'))

        share = SharedSummary(
            summary_id   = form.summary_id.data,
            from_user_id = current_user.id,
            to_user_id   = form.recipient_id.data
        )
        db.session.add(share)
        db.session.commit()
        flash("Summary successfully shared!", "success")
        return redirect(url_for('user.share'))

    # 4) history
    shared_by_me   = SharedSummary.query.filter_by(from_user_id=current_user.id).all()
    shared_with_me = SharedSummary.query.filter_by(to_user_id=current_user.id).all()

    return render_template(
        'user/share_data.html',
        form            = form,
        shared_by_me    = shared_by_me,
        shared_with_me  = shared_with_me
    )

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
        print("Attempting to create Summary with CGT:", total_cgt)
        new_summary = Summary(
            user_id    = current_user.id,
            total_cgt  = total_cgt,
            filename   = filename
        )
        db.session.add(new_summary)
        db.session.commit()

        print("Summary saved with ID:", summary.id)

        flash("CSV file processed successfully!")
        flash(f"Total CGT: ${total_cgt}", "info")
        return redirect(url_for('dashboard'))

    except Exception as e:
        logging.exception(f"Error processing CSV: {e}")
        flash("Failed to process CSV. Check format or logs.", "danger")
        return redirect(url_for('user.file_upload'))

    @user.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash(msg.CSRF_FAILED, 'danger')
        return redirect(request.url or url_for('index'))
