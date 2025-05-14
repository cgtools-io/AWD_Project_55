import sys
import shutil, os, stat

#Ensure Python can find the 'app' module when running pytest from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
UPLOAD_DIR = os.path.join('app', 'static', 'uploads')

import pytest
from app import create_app
from app.models import User, Summary
from app.extensions import db
import app.constants as msg
from config import TestConfig

class UserSession:
    def __init__(self, client):
        self._client = client

    def login(self, username="myusername", password="mypassword0!"):
        return self._client.post("/login", data={
            "username": username, 
            "password": password
            }, follow_redirects=True
        )
    def logout(self):
        return self._client.get("/logout", follow_redirects=True)

@pytest.fixture
def app():
    app = create_app(config_class=TestConfig)
    
    assert "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"], "NOT using a test DB!"

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username=msg.TEST_USER, email=msg.TEST_EMAIL)
        user.set_password(msg.TEST_PASSWORD)
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth(client):
    return UserSession(client)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_upload_folder():
    if os.path.exists(UPLOAD_DIR):
        os.chmod(UPLOAD_DIR, stat.S_IRWXU)
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield

@pytest.fixture
def two_users(app):
    user1 = User(username="james",   email="james@example.com")
    user1.set_password("pw1")

    user2 = User(username="sacha", email="sacha@example.com")
    user2.set_password("pw2")

    db.session.add_all([user1, user2])
    db.session.commit()

    return user1, user2

@pytest.fixture
def some_summaries(app, two_users):
    james, _ = two_users

    s1 = Summary(user_id=james.id, total_buy=100, total_sell=200)
    s2 = Summary(user_id=james.id, total_buy=300, total_sell=400)

    db.session.add_all([s1, s2])
    db.session.commit()

    return [s1, s2]