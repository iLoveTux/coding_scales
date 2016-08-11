import os
import flask
from functools import wraps
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask,
                   current_app,
                   render_template,
                   redirect,
                   url_for,
                   flash,
                   request)
from flask_login import (current_user,
                         login_user,
                         LoginManager)
from flask_restless import (APIManager,
                            ProcessingException)

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

db = SQLAlchemy(app)

# api_manager = APIManager(app, flask_sqlalchemy_db=db)

def configure_app(debug=False,
                  testing=False,
                  db_uri="sqlite:///coding_scales.db"):

    app.config['DEBUG']                   = debug
    app.config['TESTING']                 = testing
    if testing:
        app.test_request_context().push()
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    return app


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return current_app.login_manager.unauthorized()
            urole = current_app.login_manager.reload_user().get_urole()
            if ( (urole != role) and (role != "ANY")):
                return current_app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    email = db.Column(db.String(80), unique=True, index=True)
    password = db.Column(db.String(80))
    exercises = db.relationship("Exercise", backref="author", lazy="dynamic")

    def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password = password
        self.authenticated = True

    def is_active(self):
    #all users are active
        return True

    def get_id(self):
        # returns the user e-mail. not sure who calls this
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        # False as we do not support annonymity
        return False

class Exercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, author_id):
        self.author_id = author_id

class Collection(db.Model):
    __tablename__ = "collections"
    id = db.Column(db.Integer, primary_key=True)
