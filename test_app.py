import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


# ---------------- LOGIN TESTS ----------------
def test_login_page_loads(client):
    """Check that the login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200


def test_login_invalid_credentials(client):
    """Check invalid login credentials show error message."""
    response = client.post('/login', data={
        'email': 'fake@example.com',
        'password': 'wrong'
    }, follow_redirects=True)
    assert b'Invalid' in response.data or b'Invalid credentials' in response.data


# ---------------- CONTACT PAGE TESTS ----------------
def test_contact_page_loads(client):
    """Check that the Contact Us page loads."""
    response = client.get('/contactUs')
    assert response.status_code == 200


def test_contact_form_submission(client):
    """Check POST contact form submission."""
    response = client.post('/contact', data={
        'name': 'Tanmay',
        'mail': 'tanmay@example.com',
        'mob': '9876543210',
        'query': 'Testing contact form'
    }, follow_redirects=True)
    # Should redirect to home after successful insert
    assert response.status_code == 200


# ---------------- BOOK APPOINTMENT TESTS ----------------
def test_book_appointment_page_loads(client):
    """Check that the Book Appointment page loads."""
    response = client.get('/BookAppointment')
    assert response.status_code == 200


def test_book_appointment_form_submission(client):
    """Check POST Book Appointment form submission."""
    response = client.post('/BookAppointment', data={
        'name': 'Tanmay',
        'phone': '9876543210',
        'vehicle': 'Yamaha MT07',
        'date': '2025-10-10',
        'time': '10:00:00',  # ✅ valid MySQL TIME format
        'area': 'Kothrud',
        'city': 'Pune',
        'state': 'Maharashtra',
        'post-code': '411038',
        'driving_license': 'MH14-12'  # ✅ shorter string
    }, follow_redirects=True)
    assert response.status_code == 200

