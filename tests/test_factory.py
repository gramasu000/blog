from flaskr import create_app

def test_config():
    """
    Checks that the app factory, by default, returns an app that is not in testing configuration
    Checks that the app factory, with the right parameters, returns the an app that is in testing configurations
    """
    assert not create_app().testing
    assert create_app({'TESTING' : True}).testing

def test_hello(client):
    """
    Checks that the /hello endpoint outputs hello world
    """
    response = client.get("/hello");
    assert response.data == b"Hello World!"
