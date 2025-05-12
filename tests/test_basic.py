import pytest


# -------------------------------
# Sanity check
# -------------------------------
def test_always_passes():
    assert True


# -------------------------------
# Public page loads
# -------------------------------

def test_homepage(client):
    # GET /
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to CGTools' in response.data  # Landing page banner

def test_about_page_load(client):
    # GET /about
    response = client.get('/about')
    assert response.status_code == 200
    assert b'Easily calculate' in response.data  # About page tagline

def test_contact_page_load(client):
    # GET /contact
    response = client.get('/contact')
    assert response.status_code == 200
    assert b'Reach out for support' in response.data  # Contact page message


# -------------------------------
# Authentication page loads
# -------------------------------

def test_signup_page_load(client):
    # GET /signup
    response = client.get('/signup')
    assert response.status_code == 200
    assert b'Sign Up' in response.data  # Sign-up heading

def test_login_page_loads(client): 
    # GET /login
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign up here' in response.data  # Link to sign-up

# -------------------------------
# Navbar loads
# -------------------------------

def test_navbar_links_present(client):
    # GET /signup
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    assert "Home" in html
    assert "About" in html
    assert "Contact" in html






# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # GET a nonsense URL (e.g. /no-such-page) → assert a 404 status



# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # Check for custom 404 template then check for that

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # static assest (??)(If you’ve got a custom 404 template) check for a specific message or heading in the response

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # check main CSS assert status 200 

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # JS files under /static/ -> assert status 200

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # README:
#     # Setup instructions
#     # Virtualenv + requirements.txt
#     # Running tests
#     # DB setup (migrate vs create_all)

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # Production config does NOT use sqlite or default secret key

