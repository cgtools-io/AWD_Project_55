import io
import os
import shutil
import pytest
import app.constants as msg

# Directory where uploaded files should be saved
UPLOAD_DIR = os.path.join('app', 'static', 'uploads')

@pytest.fixture(autouse=True)
def clean_upload_folder():
    # Ensure a clean uploads folder before each test
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield


# -------------------------------
# Access Controls
# -------------------------------

def test_file_upload_requires_login(client):
    # unauthed users hitting /file_upload should receive 403 Forbidden
    resp = client.get('/file_upload/')
    assert resp.status_code == 403
    assert b'ERROR 403' in resp.data


def test_file_upload_page_loads_when_authenticated(client, auth, test_user):
    # Logged-in users should see the upload page
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    resp = client.get('/file_upload/')
    assert resp.status_code == 200
    assert b'Upload .csv file:' in resp.data


# -------------------------------
# Form Validation
# -------------------------------

def test_upload_no_file_shows_required_error(client, auth, test_user):
    # Submitting without selecting a file triggers a required-field error
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    resp = client.post(
        '/file_upload/',
        data={},  # no file included
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert resp.status_code == 200
    assert b'This field is required.' in resp.data


def test_upload_non_csv_shows_csv_only_error(client, auth, test_user):
    # Uploading a non-CSV should flash the CSV_ONLY message
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)
    fake_txt = {'file': (io.BytesIO(b"not,a,csv"), 'notes.txt')}
    resp = client.post(
        '/file_upload/',
        data=fake_txt,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert resp.status_code == 200
    # CSV_ONLY msg for invalid file types
    assert msg.CSV_ONLY.encode() in resp.data


# -------------------------------
# Happy Path
# -------------------------------

def test_upload_csv_happy_path(client, auth, test_user):
    # Uploading a valid CSV should flash success and save the file
    auth.login(username=msg.TEST_USER, password=msg.TEST_PASSWORD)

    # Create a simple in-memory CSV
    sample = io.BytesIO(b"col1,col2,col3\n1,2,3\n4,5,6")
    data = {'file': (sample, 'transactions.csv'),
            'broker': 'binance'}

    resp = client.post(
        '/file_upload/',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    print(resp.data)
    assert resp.status_code == 200
    # Check for the UPLOAD_SUCCESS flash
    assert msg.UPLOAD_SUCCESS.encode() in resp.data

    # Verify the file was saved in the uploads directory
    saved_files = os.listdir(UPLOAD_DIR)
    assert 'transactions.csv' in saved_files

    # or, confirm the files contents are intact
    path = os.path.join(UPLOAD_DIR, 'transactions.csv')
    with open(path, 'rb') as f:
        assert f.read().startswith(b"col1,col2,col3")
