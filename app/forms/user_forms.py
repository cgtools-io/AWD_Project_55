from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField, ValidationError
from wtforms.validators import Length, EqualTo, Email, InputRequired

from app.models import User
import app.constants as msg


class SignupForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(min=2, max=25)])
    email = EmailField('Email:', validators=[InputRequired(), Email()])
    password = PasswordField('Password:', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm password:', validators=[InputRequired(), EqualTo('password', message=msg.PASSWORD_MISMATCH)])
    submit = SubmitField('Register account')

    def validate_username(self, username):
        if current_user.is_authenticated:
            raise ValidationError(msg.ALREADY_LOGGED_IN)
        new_user = User.query.filter_by(username=username.data).first()
        if new_user:
            raise ValidationError(msg.USERNAME_TAKEN)

    def validate_email(self, email):
        if current_user.is_authenticated:
            raise ValidationError(msg.ALREADY_LOGGED_IN)
        new_email = User.query.filter_by(email=email.data).first()
        if new_email:
            raise ValidationError(msg.EMAIL_REGISTERED)

class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(min=2, max=25)])
    password = PasswordField('Password:', validators=[InputRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')