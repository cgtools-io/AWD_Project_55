# login, signup, logout, “already logged in,” redirect-when-authenticated, blank-field errors

import app.constants as msg
import uuid

# Logging in/out cases
def test_valid_user(client, test_user):
    response = client.post('/login', data={
        'username': msg.TEST_USER,
        'password': msg.TEST_PASSWORD
    }, follow_redirects=True)
    assert response.status_code == 200
    assert msg.LOGIN_SUCCESS.encode() in response.data

def test_invalid_user(client, test_user):
    response = client.post('/login', data={
        'username': 'wrong',
        'password': 'wronger'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert msg.INVALID_CREDENTIALS.encode() in response.data

def test_logout(client, auth, test_user):
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    response = client.get('/logout', follow_redirects=True)
    assert msg.LOGOUT_SUCCESS.encode() in response.data

# Registration cases
def test_register_user(client):
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    unique_email = f"{unique_user}@text.com"

    response = client.post('/signup', data={
        'username': unique_user,
        'email': unique_email,
        'password': 'securepassword',
        'confirm_password': 'securepassword',
        'submit': True
    }, follow_redirects=True)

    assert msg.ACCOUNT_CREATED.encode() in response.data

def test_duplicate_user(client, test_user):
    response = client.post("/signup", data={
        'username': msg.TEST_USER,
        'email': msg.TEST_EMAIL,
        'password': msg.TEST_PASSWORD,
        'confirm_password': msg.TEST_PASSWORD,
        'submit': True
    }, follow_redirects=True)

    assert msg.USERNAME_TAKEN.encode() in response.data


def test_protected_route_requires_login(client):
    response = client.get('/file_upload')
    assert response.status_code == 403
    assert b'ERROR 403' in response.data

# def test_missing_data(client:
#     response = client.post('/signup', data={
#         'username'



#     })
#     )

# TODO: Register with missing/invalid data
# TODO: Redirect or error handling on registration failure



# FOURTH: Access cases
# TODO: Unauthenticated user access redirects to login
# TODO: Authenticated user access succeeds


# -------------------------------
# NavBar loads and redirects
# -------------------------------

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''

# On / or /about, assert you see “Home”, “About”, “Contact” and a “Login” button

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
# # Navigation bar links (unauthenticated) route to right page