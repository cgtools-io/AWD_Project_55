import uuid

# FIRST: Pages Load
def test_login_page_loads(client): 
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_signup_page_load(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Register account" in response.data

# SECOND: Logging in/out
def test_valid_user(client, test_user):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Login successful!" in response.data

def test_invalid_user(client, test_user):
    response = client.post('/login', data={
        'username': 'wrong',
        'password': 'wronger'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username" in response.data

def test_logout(client, auth, test_user):
    auth.login(username="testuser", password="password123!")
    response = client.get('/logout', follow_redirects=True)
    assert b"You have been logged out." in response.data

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

    assert b"created successfully" in response.data

