# ========================================================================
#                       SYS PATH + CONSTANTS
# ========================================================================
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
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


# ========================================================================
#                   FLASK APP + CLIENT FIXTURES
# ========================================================================

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
def client(app):
    return app.test_client()

@pytest.fixture
def auth(client):
    return UserSession(client)


# ========================================================================
#                   USER SESSION HELPER
# ========================================================================

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


# ========================================================================
#                   ENVIRONMENT CLEANUP (Uploads Folder)
# ========================================================================

@pytest.fixture(autouse=True)
def clean_upload_folder():
    if os.path.exists(UPLOAD_DIR):
        os.chmod(UPLOAD_DIR, stat.S_IRWXU)
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield


# ========================================================================
#                   USER + SUMMARY FIXTURES
# ========================================================================

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username=msg.TEST_USER, email=msg.TEST_EMAIL)
        user.set_password(msg.TEST_PASSWORD)
        db.session.add(user)
        db.session.commit()
        return user

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

    s1 = Summary(user_id=james.id, total_cgt=100.00, filename="binance.csv")
    s2 = Summary(user_id=james.id, total_cgt=200.00, filename="kraken.csv")

    db.session.add_all([s1, s2])
    db.session.commit()

    return [s1, s2]

@pytest.fixture
def two_users_and_summary(app, two_users):
    james, sacha = two_users
    db.session.add_all([james, sacha])
    db.session.commit()

    summary = Summary(user_id=james.id, total_cgt=100.0, filename="binance.csv")
    db.session.add(summary)
    db.session.commit()

    return james, sacha, summary

# ========================================================================
#                   SELENIUM DRIVER FIXTURE (HEADLESS FIREFOX)
# ========================================================================

@pytest.fixture
def selenium_driver():
    options = Options()
    # Comment out the next line to see it in the real browser:
    options.headless = True
    options.add_argument("--headless")  
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()

@pytest.fixture()
def selenium_registered_user(selenium_driver):
    selenium_driver.get(msg.LH + "/signup")
    selenium_driver.find_element(By.NAME, "username").send_keys(msg.TEST_USER)
    selenium_driver.find_element(By.NAME, "email").send_keys(msg.TEST_EMAIL)
    selenium_driver.find_element(By.NAME, "password").send_keys(msg.TEST_PASSWORD)
    selenium_driver.find_element(By.NAME, "confirm_password").send_keys(msg.TEST_PASSWORD)
    selenium_driver.find_element(By.NAME, "submit").click()
    return {
        "username": msg.TEST_USER, 
        "password": msg.TEST_PASSWORD
    }

# ========================================================================
#                   SELENIUM HELPER FUNCTIONS (MUST IMPORT)
# ========================================================================

def selenium_login(driver, user):
    driver.get(msg.LH + "/login")
    driver.find_element(By.NAME, "username").send_keys(user["username"])
    driver.find_element(By.NAME, "password").send_keys(user["password"])
    driver.find_element(By.NAME, "submit").click()