#!/bin/bash

# Production
#export FLASK_APP=hello.py
#export FLASK_ENV=production
#flask run --host=0.0.0.0

# Development

# FLASK_APP is an environment variable
#   which tells flask what module to import 
#   at flask run
export FLASK_APP=flaskr

# FLASK_ENV is an environment variable
#   which determines what mode flask will be run
#   In development mode, the app activate the debugger,
#   and automatically reload after code changes.
export FLASK_ENV=development

# We run the flask app
flask run

