def test_always_passes():
    assert True

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to CGTools' in response.data # Landing

def test_about_page_load(client):
    response = client.get('/about')
    assert response.status_code == 200 # About
    assert b'Easily calculate' in response.data
    
def test_contact_page_load(client):
    response = client.get('/contact')
    assert response.status_code == 200 # Contact
    assert b'Reach out for support' in response.data
     
def test_signup_page_load(client):
    response = client.get('/signup')
    assert response.status_code == 200 # Signup
    assert b'Sign up here' in response.data


### TEMPLATES BELOW TO FILL OUT - WIP
# def test_login_page_loads(client): 
#     response = client.get('/login')
#     assert response.status_code == 200
#     assert b"Login" in response.data # Login

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # On / or /about, assert you see “Home”, “About”, “Contact” and a “Login” button

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
# # Navigation bar links (unauthenticated) route to right page

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
# # Verify the “Get Started” CTA link actually points to /signup

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
# # Confirm the footer text contains “© CGTools 2025”

# def test_(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b''
#  # 404 handling

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

