# -------------------------------
# Authentication page loads
# -------------------------------

import pytest
import uuid
import app.constants as msg

# Login page should load for guests
def test_login_page_loads(client):
    # Note: basic smoke test for login view
    resp = client.get('/login/')
    assert resp.status_code == 200
    assert b"Login" in resp.data

# Signup page should load for guests
def test_signup_page_load(client):
    # Note: basic smoke test for signup view
    resp = client.get('/signup/')
    assert resp.status_code == 200
    assert b"Register account" in resp.data


# -------------------------------
# Logging in/out cases
# -------------------------------

def test_valid_user(client, test_user):
    # login with correct creds pops a success flash
    resp = client.post(
        '/login/', data={
            'username': msg.TEST_USER,
            'password': msg.TEST_PASSWORD
        }, follow_redirects=True
    )
    assert resp.status_code == 200
    assert msg.LOGIN_SUCCESS.encode() in resp.data


def test_invalid_user(client, test_user):
    # wrong user/pass should flash invalid credentials
    resp = client.post(
        '/login/', data={
            'username': 'wrong',
            'password': 'wronger'
        }, follow_redirects=True
    )
    assert resp.status_code == 200
    assert msg.INVALID_CREDENTIALS.encode() in resp.data


def test_blank_login_fields(client):
    # empty username & password should trigger required-error
    resp = client.post(
        '/login/', data={
            'username': '',
            'password': ''},
        follow_redirects=True
    )
    assert resp.status_code == 200
    assert b'This field is required.' in resp.data


def test_logout(client, auth, test_user):
    # login then logout should flash LOGOUT_SUCCESS
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    resp = client.get('/logout/', follow_redirects=True)
    assert msg.LOGOUT_SUCCESS.encode() in resp.data


def test_login_redirect_if_already_authenticated(client, auth, test_user):
    # logged-in users hitting /login should get bounced home
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    resp = client.get('/login/', follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/')


# -------------------------------
# Registration cases
# -------------------------------

def test_register_user(client):
    # new user signup should flash ACCOUNT_CREATED
    used_user = f"user_{uuid.uuid4().hex[:6]}"  # random-ish
    used_email = f"{used_user}@example.com"
    resp = client.post(
        '/signup/', data={
            'username': used_user,
            'email': used_email,
            'password': 'wowsosecret',
            'confirm_password': 'wowsosecret',
            'submit': True
        }, follow_redirects=True
    )
    assert msg.ACCOUNT_CREATED.encode() in resp.data


def test_duplicate_user(client, test_user):
    # trying to reuse TEST_USER should flash USERNAME_TAKEN
    resp = client.post(
        '/signup/', data={
            'username': msg.TEST_USER,
            'email': msg.TEST_EMAIL,
            'password': msg.TEST_PASSWORD,
            'confirm_password': msg.TEST_PASSWORD,
            'submit': True
        }, follow_redirects=True
    )
    assert msg.USERNAME_TAKEN.encode() in resp.data


def test_signup_missing_fields(client):
    # leaving all signup fields empty triggers required-errors
    resp = client.post(
        '/signup/', data={
            'username':'',
            'email':'',
            'password':'',
            'confirm_password':''},
        follow_redirects=True
    )
    assert b'This field is required.' in resp.data


def test_signup_invalid_email(client):
    # bad email format should show WTForms email-validator error
    resp = client.post(
        '/signup/', data={
            'username': 'bob_bobby_bobberson',
            'email': 'not-at-bob',
            'password': 'bobbing808',
            'confirm_password': 'bobbing808'
        }, follow_redirects=True
    )
    assert b'Invalid email address' in resp.data


def test_signup_password_mismatch(client):
    # mismatched passwords flash PASSWORD_MISMATCH
    resp = client.post(
        '/signup/', data={
            'username': 'watch_me_log_in',
            'email': 'its@gonna.work',
            'password': 'almost',
            'confirm_password': 'there'
        }, follow_redirects=True
    )
    assert msg.PASSWORD_MISMATCH.encode() in resp.data


def test_signup_while_logged_in(client, auth, test_user):
    # existing session shouldn’t allow a new signup
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    resp = client.post(
        '/signup/', data={
            'username': 'someoneelse',
            'email': 'someone@example.com',
            'password': '2bornot2b',
            'confirm_password': '2bornot2b'
        }, follow_redirects=True
    )
    assert msg.ALREADY_LOGGED_IN.encode() in resp.data


# -------------------------------
# Protected-route access
# -------------------------------

def test_protected_route_requires_login(client):
    # file_upload is protected by login_required → 403
    resp = client.get('/file_upload/')
    assert resp.status_code == 403
    assert b'ERROR 403' in resp.data


def test_navbar_when_logged_in(client, auth, test_user):
    # Navbar updates when authenticated: show Logout & Tools, hide Login
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    resp = client.get('/')
    html = resp.data.decode('utf-8')
    assert 'Logout' in html
    assert 'Tools' in html
    assert 'Login' not in html
