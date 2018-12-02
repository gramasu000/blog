import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

# Open SQL code from data.sql, read it and parse it
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    """
    This function is a pytest fixture, meaning that it can be used as an object in pytest function.
    This function returns the flask app with testing configurations and a temporary fake database
    """
    # We make a temporary file for the database instance
    db_fd, db_path = tempfile.mkstemp()
    
    # We use the application factory to create the flask app and 
    #   give it a new database path and set TESTING mode to true
    #   which disables error catching.
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    
    # I don't really understand this part yet,
    #   I just will say this is how to initialize the fake db
    #   connect to it, and close the connection after the tests 
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """
    This function is a pytest fixture, meaning that it can be used as an object in pytest function.
    This function returns a client object, like a weak headless browser.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    This function is a pytest fixture, meaning that it can be used as an object in pytest function.
    This function returns a runner, whatever that is 
    """
    return app.test_cli_runner()

class AuthActions(object):
    """
    This class uses the client fixture to login and logout from the app.
    """
    def __init__(self, client):
        """
        Constructor to initialize the client fixture as a class property
        """
        self._client = client
    
    def login(self, username="test", password="test"):
        """
        Login Method - Client goes to login endpoint and posts username and password.
        """
        return self._client.post(
            "/auth/login", 
            data={"username": username, "password": password}
        )

    def logout(self):
        """
        Logout Method - Client goes to logout endpoint (HTTP GET)
        """
        return self._client.get("/auth/logout")

@pytest.fixture
def auth(client):
    """
    This function is a pytest fixture, meaning that it can be used as an object in pytest function.
    This function returns the class AuthActions, which uses the client fixture to login and logout from the app 
    """
    return AuthActions(client)
