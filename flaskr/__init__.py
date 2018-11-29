import os
from flask import Flask

def create_app(test_config=None):
    """
    Application Factory Function
    Creates the Flask instance, configures it and returns it
    This is better than having the Flask instance as a global variable.
    """

    # When creating the flask instance,
    #   we pass in the module name __name__
    #   and we tell Flask to search in instance/ directory
    #   for database and config files private to the website. 
    app = Flask(__name__, instance_relative_config=True)

    # Sets up default configuration
    #   SECRET_KEY will be a key to encrypt data, set to "dev" during development
    #   DATABASE will be the path where the database instance will be stored
    #       it is set to be inside Flask instance/ directory.
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )
    
    # Loads normal configuration file in instance/ folder,
    #   or test configuration file if required.  
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure that the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # When the web url is <url>/hello, 
    #   we load a simple hello world page
    @app.route('/hello')
    def hello():
        return "<h1>Hello World!</h1>"

    # Register init_db_command and close_db from db.py file
    from . import db
    db.init_app(app)

    # Register the authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # Register the blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    # Makes sure that url_for("index") and url_for("blog.index") are same
    app.add_url_rule("/", endpoint="index")

    # Return app
    return app
