def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_signup_page_load(client):
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Register account" in response.data

def test_valid_user(client):
    response = client.post('/login', data={
        'username': 'abc',
        'password': 'abc'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Login successful!" in response.data

def test_invalid_user(client):
    response = client.post('/login', data={
        'username': 'wrong',
        'password': 'wronger'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username" in response.data

def test_logout(client, auth):
    auth.login()
    response = client.get('/logout', follow_redirects=True)
    assert b"You have been logged out." in response.data

def test_register_user(client):
    response = client.post('/signup', data={
        'username': 'newuser',
        'email': 'new@user.com',
        'password': 'securepassword',
        'confirm_password': 'securepassword',
        'submit': True
    }, follow_redirects=True)
    assert b"created successfully" in response.data