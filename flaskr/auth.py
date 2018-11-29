import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# Blueprint object for website authentication
bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=("GET", "POST"))
def register():
    """
    This function is linked to /auth/register url
        If request method is post, this means that the user
            filled out the username-password HTML form
            so the function checks the user input
            and redirect to login if the input is valid
        If the request method is get, then the user
            is just getting to the register view
            so we just serve the HTML page with the 
                username-password HTML form.
    """
    # If request method is post, this means that
    #   the user submitted the HTML form in the view
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        
        # Check if the username is filled out
        if not username:
            error = "Username is required."
        # Check if the password is filled out
        elif not password:
            error = "Password is required."
        # Check if anyone else has same username
        elif db.execute(
            "SELECT id from user WHERE username = ?", (username, )
        ).fetchone() is not None:
            error = "User {} is already registered.".format(username)

        # If input is valid, then we create a username and password
        #   in the database and redirect the user to login page
        if error is None:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?,?)",
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for("auth.login"))

        # If the input is invalid, we store error in flash object
        #   to show in template
        flash(error)
    
    # If HTML request is GET, then we serve the view as normal 
    return render_template("auth/register.html")
        
@bp.route("/login", methods=("GET", "POST"))
def login():
    """
    This function is linked to the /auth/login url.
        If the request method is POST,
            this means the user has entered in
                a username and password,
            so the function checks the input
            and redirects to index page if the input is valid
    If the request method is GET,
        then the function just serves the login page
    """
    
    # If the request method is POST
    #   then it means the user has filled out the form
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        # Check if username exists
        if user is None:
            error = "Incorrect username."
        # Check if password is correct
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        
        # If input is valid, store the user's id on a session object
        #   redirect the user to index page.         
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        
        # If input is not valid, store the error message in flash object
        #   to use in template
        flash(error)
    
    # If request method is GET, then we simply serve the login view
    return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
    """
    This function will transfer user information
    from session object to g object. 
    If user is not logged in, session.user and g.user are both None
    """
    # Get the user id from session object
    user_id = session.get("user_id")
    
    # If user id is None, g.user is also None
    if user_id is None:
        g.user = None
    # If user id is not None, we pull all data for that user
    #   from the database and store that in g.user
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id, )
        ).fetchone()

@bp.route("/logout")
def logout():
    """
    Logout function
    When the user logs out, we clear the session
    and redirect to index page
    """
    session.clear()
    return redirect(url_for("index"))

def login_required(view):
    """
    This function is a decorator.
    For every function with @login_required on top of it,
        this function will be called first and then that function will be called.
    This function just checks to see if the user is logged on
        before displaying the view
    """
    @functools.wraps(view)
    # Make a wrapper view that encapsulates the normal view,
    #   with the extra condition of checking g.user is not None
    def wrapped_view(**kwargs):
        # If g.user is none, we redirect to login page
        if g.user is None:
            return redirect(url_for("auth.login"))
        # Return view if g.user has information
        return view(**kwargs)

    # return wrapper view
    return wrapped_view
