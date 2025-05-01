from flask import Blueprint, request, jsonify, url_for, render_template, flash, redirect, session, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
import logging

from app.extensions import db
from app.forms.user_forms import SignupForm

user = Blueprint('user', __name__)

logger = logging.getLogger(__name__)

@user.route('/signup', methods=['GET', 'POST'])
def signup():
    logging.debug("User signup endpoint accessed")

    form = SignupForm()

    return render_template('auth/signup.html', form=form)