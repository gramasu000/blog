import sqlite3

import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    """
    Checks that get_db outputs the same connection each time it is called.
    Checks that connection is closed after the context
    """
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e)

def test_init_db_command(runner, monkeypatch):
    """
    Checks to see if flask init-db command actually runs init_db function
    """
    class Recorder(object):
        called = False
    
    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
