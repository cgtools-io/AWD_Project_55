import sys
import shutil, os, stat

#Ensure Python can find the 'app' module when running pytest from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
UPLOAD_DIR = os.path.join('app', 'static', 'uploads')

import pytest
from app import create_app
from app.models import User
from app.extensions import db
import app.constants as msg

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
    app.config['TRAP_HTTP_EXCEPTIONS'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = False

    with app.app_context():
        from app.extensions import db
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
        os.chmod(UPLOAD_DIR, stat.S_IWUSR)
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield