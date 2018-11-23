import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    """
    Creates a connection to the database instance
        in the instance/ directory.
    Returns the database object
    Also attaches it to global object g
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        
        # Rows in sqlite will be dicts in python
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """
    Checks if database object exists in g
        if it does, it is popped from g and closed
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db():
    """
    Create a db object using get_db
        and run sql code in schema.sql to create tables
    """
    db = get_db();
    
    # Use current_app.open_resource to open a file relative to flask app
    #   Use read() decode() and executescript to 
    #       to interpret text as sql instructions 
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))

@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    This function initializes the db using init_db
        and prints a message to console.
    The function is linked to a newly created flask command init-db
        by the @click.command/@with_appcontext decorators
    """
    init_db()
    click.echo("Initialized the database")

def init_app(app):
    """
    We register the close_db and init_db_command with the application 
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
