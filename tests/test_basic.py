import pytest


# -------------------------------
# Sanity check
# -------------------------------
def test_always_passes():
    assert True

def test_secret_key_not_default(app):
    assert app.config["SECRET_KEY"] != "default-secret"


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
    assert b'A friendly' in response.data  # About page tagline

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

# -------------------------------
# Static files load            TODO: add svg folder when merged
# -------------------------------

def test_css_style_sheet_loads(client):
    response = client.get('/static/css/style.css')
    assert response.status_code == 200

def test_javascript_script_loads(client):
    response = client.get('/static/js/script.js')
    assert response.status_code == 200
