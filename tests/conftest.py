import sys
import os

#Ensure Python can find the 'app' module when running pytest from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.models import User
from app.extensions import db

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
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # disabled CSRF for testing POSTs
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" # temp DB for testing

    with app.app_context():
        from app.extensions import db
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    return app

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username="testuser", email="user@test.com")
        user.set_password("password123!")
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth(client):
    return UserSession(client)

@pytest.fixture
def client(app):
    return app.test_client()