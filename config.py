import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = 'sqlite:///' + os.path.join(basedir, 'app.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or default_db_path
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-private-key'