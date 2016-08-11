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

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

api_manager = APIManager(app, flask_sqlalchemy_db=db)

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
    date_joined = db.Column(db.DateTime, nullable=False)
    billing_date = db.Column(db.Integer, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    role = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80))
    exercises = db.relationship("Exercise", backref="author", lazy="dynamic")
    results = db.relationship("Result", backref="user", lazy="dynamic")

    def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password = password
        self.authenticated = True
        self.verified = True
        self.role = "user"
        self.date_joined = datetime.now()
        self.billing_date = self.date_joined.day

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
    name = db.Column(db.String(80), nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime)
    language = db.Column(db.String(80), nullable=False)
    results = db.relationship("Result", backref="exercise", lazy="dynamic")

    def __init__(self, author_id, text, language, name):
        self.author_id = author_id
        self.text = text
        self.language = language.lower()
        self.name = name.lower()
        self.date_added = datetime.now()

class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    time = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, exercise_id, time):
        self.user_id = user_id
        self.exercise_id = exercise_id
        self.time = time
        self.date = datetime.now()

api_manager.create_api(
    User,
    methods=["GET", "POST", "PUT", "DELETE"],
    # preprocessors=dict(GET_SINGLE=[admin_required],
    #                    GET_MANY=[admin_required]),
    # deserializer=user_deserializer,
    include_columns=["username",
                     "id",
                     "role",
                     "date_joined",
                     "billing_date",
                     "verified",
                     "exercises",
                     "results"]
)

api_manager.create_api(
    Exercise,
    methods=["GET", "POST", "PUT", "DELETE"],
    # preprocessors=dict(GET_SINGLE=[auth_func],
    #                    GET_MANY=[auth_func]),
    # deserializer=exercise_deserializer,
    include_columns=["name",
                     "id",
                     "language",
                     "date_added",
                     "author",
                     "text"]
)
api_manager.create_api(
    Result,
    methods=["GET", "POST", "PUT"],         #, "DELETE"],
    # preprocessors=dict(GET_SINGLE=[auth_func],
    #                    GET_MANY=[auth_func]),
    # deserializer=result_deserializer,
    include_columns=["id",
                     "user_id",
                     "exercise_id",
                     "time",
                     "date"]
)
