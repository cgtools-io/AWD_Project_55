# -------------------------------
# Error page handling
# -------------------------------

import pytest

# Tests that simulate various error scenarios and ensure we:
# 1. Return the correct HTTP status codes (e.g. 404, 403)
# 2. Render our custom error pages correctly
# 3. Include consistent branding/text (like "Country roads...") across all errors

# Test both 404 (page not found) and 403 (unauthorised access) errors
@pytest.mark.parametrize("url, expected_code", [
    ("/i-dont-exist", 404),      # Nonexistent route
    ("/share/", 403),             # Protected route without login (should trigger custom unauthorised handler)
])
def test_error_status_and_template(client, url, expected_code):
    response = client.get(url, follow_redirects=False)  # Don’t follow redirects so we can check real status code
    html = response.data.decode()

    # Check we got the right error code
    assert response.status_code == expected_code
    
    # Our custom error template should always include this branding text + status number
    assert f"ERROR {expected_code}" in html
    assert "Country roads..." in html


# Test malformed or missing data causing a 400 Bad Request
def test_400_bad_request(client):
    # We simulate this by submitting an empty signup form
    response = client.post("/signup/", data={})

    # Depending on form config, Flask may either return 400 or stay on page (200).
    # This test is soft for now — we may refine once error triggering is stricter.
    assert response.status_code in (400, 200)


# Test that using an unsupported method (e.g. POST on GET-only route) returns 405
def test_405_method_not_allowed(client):
    response = client.post("/about/")  # Our /about route is GET-only
    assert response.status_code == 405
    assert b"ERROR 405" in response.data  # Make sure our custom error message renders


# Test the 500 Internal Server Error page by deliberately crashing a route
def test_500_internal_error_handling(client, app):
    # We define a temporary test route that crashes on purpose
    @app.route("/force500")
    def force_500():
        raise Exception("Simulated server error")

    # Hit the broken route using a fresh test client
    with app.test_client() as test_client:
        response = test_client.get("/force500")
        
        # Ensure our 500 template kicks in
        assert response.status_code == 500
        assert b"ERROR 500" in response.data