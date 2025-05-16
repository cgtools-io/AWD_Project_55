# Setup and Installation

---

#### **Create and activate a virtual environment**

#### Create venv
```python3 -m venv venv```

#### Activate
##### _Mac/Linux_
```source venv/bin/activate```
 
##### _Windows_
```.\venv\Scripts\activate```

#### **Install requirements**

```pip install -r requirements.txt```

#### **Activate Live Environment (launches an isolated test server)**

```python test_run.py```

### Selenium Tests

_Run in a separate terminal, with the test server already running_
```pytest tests/test_selenium.py -v```

### Unit Tests
_Run in a separate terminal (or shut down the test server first)_
```pytest --ignore=tests/test_selenium.py```

---

### **What the Selenium Test Covers**
The full test flow simulates:

- Registering a user
- Logging in
- Visiting the file upload page
- Interacting with the broker selection and upload form
- Triggering validation errors
- Submitting a valid file
- Verifying the flash message
- Visiting the Share page to check the file was saved

---

### **What the Unit Test Covers**
#### test_basic.py
- Sanity check (test runner is working)
- SECRET_KEY is not left as default
- Public pages load: /, /about, /contact
- Auth pages load: /signup, /login
- Navbar contains Home, About, Contact links
- Static CSS and JS files load correctly

#### test_errors.py
- error
  - 400
  - 403
  - 404
  - 405
  - 500

#### test_file_upload.py
- Requires login to access `/file_upload/` (unauthenticated users get `403`)
- Authenticated users can load the upload page
- Submitting the form without a file shows a **required field** error
- Uploading a non-CSV file shows a **CSV-only allowed** error
- Uploading a valid CSV:
  - Flashes the **upload success** message
  - Saves the file to the correct uploads directory
  - Verifies contents of the saved file are correct

#### test_user_actions.py
- Login and signup pages load correctly
- Successful login with valid credentials
- Login fails with:
  - Wrong credentials
  - Blank form fields
- Logout flashes a success message
- Logged-in users are redirected away from the login page
- New user registration succeeds and flashes success
- Registration fails with:
  - Duplicate username
  - Missing fields
  - Invalid email format
  - Mismatched passwords
  - While already logged in
- Protected routes (like `/file_upload/`) are blocked when not logged in
- Navbar updates after login (shows Logout/Tools, hides Login)

---

### **⚙️ Notes**

- Tests use an **in-memory database** (sqlite:///:memory:) and do **not** persist or affect real data.
    
- CSRF protection is disabled during testing via TestConfig.
    
- The test runs in **headless Firefox** by default (invisible browser); you can disable this in tests/conftest.py if needed for debugging.

- All tests import constants.py for reusability
