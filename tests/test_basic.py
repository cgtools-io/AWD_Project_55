def test_always_passes():
    assert True

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200

