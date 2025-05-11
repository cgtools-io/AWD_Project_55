import app.constants as msg
import uuid

# FIRST: Pages Load cases
def test_login_page_loads(client): 
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_signup_page_load(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Register account" in response.data

# SECOND: Logging in/out cases
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

# THIRD: Registration cases
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

# TODO: Unauthenticated user access redirects to login
# TODO: Authenticated user access succeeds
# TODO: Register with missing/invalid data
# TODO: Redirect or error handling on registration failure