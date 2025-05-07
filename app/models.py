from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Admin(UserMixin):
    def __init__(self, id=None, username=None):
        self.id = id
        self.username = username
        self.role = 'admin'
        self.password_hash = None
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return True

# TODO: This model structure is based on placeholder headers. Adjust fields/types once final format is known.
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # tie it to a user if needed
    date = db.Column(db.String)
    asset = db.Column(db.String)
    type = db.Column(db.String)
    quantity = db.Column(db.Float)
    price = db.Column(db.Float)
    fee = db.Column(db.Float)
    exchange = db.Column(db.String)
    notes = db.Column(db.Text)