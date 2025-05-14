from datetime import datetime
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

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True) # makes sure there is an associated user_id for each summary
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id'), 
        nullable=False
        ) 

    total_buy = db.Column(db.Float)
    total_sell = db.Column(db.Float)

class SharedSummary(db.Model):
    __tablename__ = 'shared_summary'
    
    id = db.Column(db.Integer, primary_key = True) # just to simplify queries if needed

    # links to summary id
    summary_id = db.Column(
        db.Integer,
        db.ForeignKey('summary.id'),
        nullable=False
    )

    from_user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    to_user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    # mostly for debugging, unsure if this will feature in actual sharing
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )




