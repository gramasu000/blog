import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    """
    Checks that registration endpoint exists, 
        that after submitting username-password that it redirects to login page
        and that username-password exists in the database 
    """
    assert client.get("/auth/register").status_code == 200
    response = client.post(
        "/auth/register", data={"username":"a", "password":"a"}
    )
    assert "http://localhost/auth/login" == response.headers["Location"]

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

@pytest.mark.parametrize(("username", "password", "message"), (
    ("", "", b"Username is required."),
    ("a", "", b"Password is required"),
    ("test", "test", b"already registered"),
))
def test_register_validate_input(client, username, password, message):
    """
    Checks that the following error checks work
        - username is required, 
        - password is required 
        - username-password already registered
    """
    response = client.post(
        "/auth/register",
        data={"username":username, "password": password}
    )
    assert message in response.data

def test_login(client, auth):
    """
    Checks that login endpoint exists, we are redirected to / endpoint,
        after logging in, and the session and g username variables have the right values
    """
    assert client.get("/auth/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "http://localhost/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"

@pytest.mark.parametrize(("username", "password", "message"), (
    ("a", "test", b"Incorrect username."),
    ("test", "a", b"Incorrect password."),
))
def test_login_validate_input(auth, username, password, message):
    """
    Checks that the following error checks work
        - username is incorrect
        - password is incorrect
    """
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    """
    Checks that logout clears session
    """
    auth.login()
    
    with client:
        auth.logout()
        assert "user_id" not in session


