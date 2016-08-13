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
                         LoginManager,
                         UserMixin)
from flask_restless import (APIManager,
                            ProcessingException)

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///coding_scales.db"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

api_manager = APIManager(app, flask_sqlalchemy_db=db)

def configure_app(debug=False,
                  testing=False,
                  **kwargs):
                  #db_uri=None):
    global app
    app.config['DEBUG']                   = debug
    app.config['TESTING']                 = testing
    if testing:
        app.test_request_context().push()
    # if db_uri:
    #     app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    return app


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            urole = current_user.role
            if ( (urole != role) and (role != "ANY")):
                return current_app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, index=True, nullable=False)
    email        = db.Column(db.String(80), unique=True, index=True, nullable=False)
    date_joined  = db.Column(db.DateTime, nullable=False)
    billing_date = db.Column(db.Integer, nullable=False)
    verified     = db.Column(db.Boolean, nullable=False)
    role         = db.Column(db.String(80), nullable=False)
    password     = db.Column(db.String(80), nullable=False)
    exercises    = db.relationship("Exercise", backref="author", lazy="dynamic")
    results      = db.relationship("Result", backref="user", lazy="dynamic")

    def __init__(self, username=None, email=None, password=None):
        self.username      = username
        self.email         = email
        self.password      = password
        # self.authenticated = True
        self.verified      = True
        self.role          = "user"
        self.date_joined   = datetime.now()
        self.billing_date  = self.date_joined.day

    # # def is_active(self):
    # # #all users are active
    # #     return True

    # def get_id(self):
    #     return self.id

    # def is_authenticated(self):
    #     return self.authenticated

    # def is_anonymous(self):
    #     # False as we do not support annonymity
    #     return False

class Exercise(db.Model):
    __tablename__ = "exercises"
    id            = db.Column(db.Integer, primary_key=True)
    author_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name          = db.Column(db.String(80), nullable=False, unique=True)
    text          = db.Column(db.Text, nullable=False)
    date_added    = db.Column(db.DateTime, nullable=False)
    language      = db.Column(db.String(80), nullable=False)
    results       = db.relationship("Result", backref="exercise", lazy="dynamic")

    def __init__(self, author_id, text, language, name):
        self.author_id  = author_id
        self.text       = text
        self.language   = language.lower()
        self.name       = name.lower()
        self.date_added = datetime.now()

class Result(db.Model):
    __tablename__ = "results"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_id   = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    time          = db.Column(db.Integer, nullable=False)
    date          = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, exercise_id, time):
        self.user_id = user_id
        self.exercise_id = exercise_id
        self.time = time
        self.date = datetime.now()

def auth_func(**kw):
    # with open("/tmp/debug.log", "w") as fp:
    #     fp.write("HERE", str(current_user))
    if not current_user.is_authenticated:
        auth = request.authorization
        if not auth:
            raise ProcessingException(description='Not Authorized', code=401)
        matches = User.query.filter_by(username=auth.username,
                                       password=auth.password).all()
        if not len(matches) > 0:
            raise ProcessingException(description='Not Authorized', code=401)

def admin_required(**kw):
    if not current_user.is_authenticated:
        auth = request.authorization
        if not auth:
            raise ProcessingException(description='Not Authorized', code=401)
        matches = User.query.filter_by(username=auth.username,
                                       password=auth.password).all()
        if not len(matches) > 0:
            raise ProcessingException(description='Not Authorized', code=401)

        role = matches[0].role
        if (role != "admin"):
            raise ProcessingException(description='Not Authorized', code=401)

def post_exercises(search_params=None, **kw):
    filt = dict(name="author_id", op="eq", val=current_user.id)
    if not "filters" in search_params:
        search_params["filters"] = []
    search_params["filters"].append(filt)

def post_exercises(search_params=None, **kw):
    filt = dict(name="author_id", op="eq", val=current_user.id)
    if not "filters" in search_params:
        search_params["filters"] = []
    search_params["filters"].append(filt)

def private_result(search_params=None, **kw):
    filt = dict(name="user_id", op="eq", val=current_user.id)
    if not "filters" in search_params:
        search_params["filters"] = []
    search_params["filters"].append(filt)

api_manager.create_api(
    User,
    methods=["GET", "POST", "PUT", "DELETE"],
    preprocessors={"GET_SINGLE":    [auth_func],
                   "GET_MANY":      [auth_func],
                   "POST":          [admin_required],
                   "PATCH_SINGLE":  [admin_required],
                   "PATCH_MANY":    [admin_required],
                   "DELETE_SINGLE": [admin_required],
                   "DELETE_MANY":   [admin_required]},
   # deserializer=user_deserializer,
    include_columns=["username",
                     "id",
                     "date_joined",
                     "exercises",
                     "results"]
)

api_manager.create_api(
    Exercise,
    methods=["GET", "POST", "PUT", "DELETE"],
    preprocessors={"GET_SINGLE":    [auth_func],
                   "GET_MANY":      [auth_func],
                   "POST":          [auth_func],
                   "PATCH_SINGLE":  [auth_func],
                   "PATCH_MANY":    [auth_func],
                   "DELETE_SINGLE": [auth_func],
                   "DELETE_MANY":   [auth_func]},
    # deserializer=exercise_deserializer,
    include_columns=["name",
                     "id",
                     "language",
                     "date_added",
                     "author_id",
                     "text",
                     "results"]
)
api_manager.create_api(
    Result,
    methods=["GET", "POST", "PUT", "DELETE"],
    preprocessors={"GET_SINGLE":    [auth_func],
                   "GET_MANY":      [auth_func],
                   "POST":          [auth_func],
                   "PATCH_SINGLE":  [auth_func],
                   "PATCH_MANY":    [auth_func],
                   "DELETE_SINGLE": [auth_func],
                   "DELETE_MANY":   [auth_func]},
#    deserializer=result_deserializer,
    include_columns=["id",
                     "user_id",
                     "exercise",
                     "time",
                     "date"]
)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        #
        # you would check username and password here...
        #
        username, password = request.form["username"], request.form["password"]
        matches = User.query.filter_by(username=username,
                                       password=password).all()
        if len(matches) > 0:
            login_user(matches[0])
            return redirect(url_for('index'))
        flash('Username and/or password incorrect')
    return render_template('login.html')

@app.route("/")
@login_required()
def index():
    return render_template("index.html")
