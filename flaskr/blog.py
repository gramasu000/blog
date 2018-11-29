from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

# Blueprint object for blogposts - note we do not have a url_prefix
bp = Blueprint("blog", __name__)

@bp.route("/")
def index():
    """
    This function is linked to the / url or index url,
        and it shows all the blogposts
    """
    db = get_db()
    # Gets the entire blog information and user information
    #   ordered by most recent first 
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    # Render the template
    return render_template("blog/index.html", posts=posts)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """
    This function corresponds to the /create url,
        for the user to create posts.
    If the user has created a post and submitting, then we 
        check the post details if valid, and 
        we store the post and redirect to the index page
    If the post is not valid, we flash an error, and if
        the user is entering the url for the first time, we 
        simply serve the page.
    """
    # If the user request method is POST
    if request.method == "POST":
        # We save the contents of the form
        title = request.form["title"]
        body = request.form["body"]
        error = None

        # We check if there is a title.
        if not title:
            error = "Title is required."
        
        # If input is not valid, we save an error message to flash
        #   to be flashed onto a template.
        if error is not None:
            flash(error)
        # If input is valid, we insert the post details to database
        # and redirect user to index page 
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for("blog.index"))

    # If the user request method is GET, then we simply serve the view.
    return render_template("blog/create.html")

def get_post(id, check_author=True):
    """
    Retrieves a post from the database and 
        checks whether the post exists 
        and if the user wrote it
    """
    # Queries database for a post
    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?", 
        (id, )
    ).fetchone()
    
    # If post does not exists, abort with 404 error
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    # If the post does exists but the author does not match
    #   then abort with 403 error
    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """
    This function is used for updating a post for /id/update url
    We query for the post, and then, 
        if the user didn't update the post and is just arriving at the url,
        we serve him the view and if he updates the post and submits,
        we update the post in the database and redirect to the index page.
    """
    # Get post information
    post = get_post(id)
    
    # If the request method is POST, we store the form values,
    #   we update the post in the database, and redirect
    if request.method == "POST":
        # Store post in variables
        title = request.form["title"]
        body = request.form["body"]
        error = None

        # Check if title exists
        if not title:
            error = "Title is required."

        # If input is not valid, we store error message in flash object for
        #   template rendering
        if error is not None:
            flash(error)
        # If input is valid, we update the database entry and redirect
        #   to index endpoint
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?"
                " WHERE id = ?",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))
    
    # If the request method is GET, we just serve the update view
    return render_template("blog/update.html", post=post) 

@bp.route("/<int:id>/delete", methods=("POST", ))
@login_required
def delete(id):
    """
    This function corresponds to the /id/delete/ url
        and it deletes the post and redirects to index
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
