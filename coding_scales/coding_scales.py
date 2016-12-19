import statistics
import os
from functools import wraps
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask import (Flask,
				   current_app,
				   render_template,
				   redirect,
				   url_for,
				   flash,
				   request,
				   abort,
				   jsonify)
from flask_login import (current_user,
						 login_user,
						 logout_user,
						 LoginManager,
						 UserMixin)
from flask_restful import (reqparse,
						   abort,
						   Api,
						   Resource,
						   fields,
						   marshal_with)
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from io import StringIO

from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


def login_required(role="ANY"):
	"""marks a request as needing authorization, authorization can
	be provided by loging in via the web app or by providing basic
	auth.
	"""
	def wrapper(fn):
		@wraps(fn)
		def decorated_view(*args, **kwargs):
			user = current_user
			if not current_user.is_authenticated:
				auth = request.authorization
				if not auth:
					abort(401)
				matches = User.query.filter_by(username=auth.username,
											   password=auth.password).all()
				if not len(matches) > 0:
					abort(401)
				user = matches[0]
			urole = user.role
			if ( (urole != role) and (role != "ANY")):
				abort(401)
			return fn(*args, **kwargs)
		return decorated_view
	return wrapper

def current_user_or_basic_auth():
	user = current_user
	if not current_user.is_authenticated:
		auth = request.authorization
		if not auth:
			abort(401)
		user = User.query.filter_by(username=auth.username,
									password=auth.password).first()
		if not user:
			abort(401)
	return user
##################
# INITIALIZATION #
##################

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///coding_scales.db"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

api = Api(app)

@login_manager.user_loader
def load_user(userid):
	return User.query.get(userid)

##########
# MODELS #
##########

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
		self.verified      = True
		self.role          = "user"
		self.date_joined   = datetime.now()
		self.billing_date  = self.date_joined.day

class Exercise(db.Model):
	__tablename__ = "exercises"
	id            = db.Column(db.Integer, primary_key=True)
	name          = db.Column(db.String(80), nullable=False)
	date_added    = db.Column(db.DateTime, nullable=False)
	language      = db.Column(db.String(80), nullable=False)
	text          = db.Column(db.Text, nullable=False)
	author_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
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
	keypresses    = db.Column(db.Integer, nullable=False)
	time          = db.Column(db.Integer, nullable=False)
	date          = db.Column(db.DateTime, nullable=False)

	def __init__(self, exercise_id, time, keypresses, user_id):
		self.user_id     = user_id
		self.exercise_id = exercise_id
		self.time        = time
		self.keypresses  = keypresses
		self.date        = datetime.now()


#######
# API #
#######

user_fields = {
	"id":          fields.Integer,
	"username":    fields.String,
	"email":       fields.String,
	"date_joined": fields.DateTime,
}
exercise_fields = {
	"name":       fields.String,
	"id":         fields.Integer,
	"language":   fields.String,
	"date_added": fields.DateTime,
	"author_id":  fields.Integer,
	"text":       fields.String
}
result_fields = {
	"id":          fields.Integer,
	"time":        fields.Integer,
	"keypresses":  fields.Integer,
	"user_id":     fields.Integer,
	"exercise_id": fields.Integer
}

class UserAPI(Resource):
	"""Allows GET, DELETE and PUT on a single User. Only allows user to
	affect their own profile and admins can affect anyones.
	"""
	@login_required()
	@marshal_with(user_fields)
	def get(self, id):
		"""Get a user by id and return allowable fields in json format.

		Requires authentication.
		"""
		user = User.query.get_or_404(id)
		return user

	@login_required()
	@marshal_with(user_fields)
	def delete(self, id):
		"""Deletes a user by id, then returns the json representation of the
		deleted user.

		Admins can delete and users can delete their own account.
		"""
		authenticated_user = current_user_or_basic_auth()
		user = User.query.get_or_404(id)
		if (user.id != authenticated_user.id) and (authenticated_user.role != "admin"):
			abort(401)
		db.session.delete(user)
		db.session.commit()
		return user

	@login_required()
	@marshal_with(user_fields)
	def put(self, id):
		"""Updates values for a user.

		Admins can update and users can update their own account.
		"""
		allowed_updates = [
			"email"
		]
		authenticated_user = current_user_or_basic_auth()
		user = User.query.get_or_404(id)
		if (user.id != authenticated_user.id) and (authenticated_user.role != "admin"):
			abort(401)
		for field in allowed_updates:
			if getattr(user, field) and request.json.get(field):
				setattr(user, field, request.json.get(field))
		db.session.commit()
		return user

class UserListAPI(Resource):
	"""Allows getting all users and creating a user.
	"""
	@login_required()
	@marshal_with(user_fields)
	def get(self):
		per_page = int(request.args.get("per_page", 25))
		page = int(request.args.get("page", 1))
		return User.query.paginate(page=page, per_page=per_page).items

	@login_required("admin")
	@marshal_with(user_fields)
	def post(self):
		required_fields = [
			"username",
			"password",
			"email"
		]
		for field in required_fields:
			if field not in request.json:
				abort(500)
		user = User(username=request.json["username"],
					password=request.json["password"],
					email=request.json["email"])
		db.session.add(user)
		db.session.commit()
		return user

class ExerciseListAPI(Resource):
	@login_required()
	@marshal_with(exercise_fields)
	def get(self):
		per_page = int(request.args.get("per_page", 25))
		page = int(request.args.get("page", 1))
		return Exercise.query.paginate(page=page, per_page=per_page).items

	@login_required()
	@marshal_with(exercise_fields)
	def post(self):
		required_fields = [
			"name",
			"language",
			"text"
		]
		authenticated_user = current_user_or_basic_auth()
		for field in required_fields:
			if field not in request.json:
				abort(500)
		exercise = Exercise(name=request.json["name"],
							language=request.json["language"].lower(),
							author_id=authenticated_user.id,
							text=request.json["text"])
		db.session.add(exercise)
		db.session.commit()
		return exercise

class ExerciseAPI(Resource):
	@login_required()
	@marshal_with(exercise_fields)
	def get(self, id):
		return Exercise.query.get_or_404(id)


class ResultsAPI(Resource):
	@login_required()
	@marshal_with(exercise_fields)
	def get(self, id):
		return Result.query.get_or_404(id)

class ResultsListAPI(Resource):
	@login_required()
	@marshal_with(result_fields)
	def get(self):
		per_page = int(request.args.get("per_page", 25))
		page = int(request.args.get("page", 1))
		return Result.query.paginate(page=page, per_page=per_page).items

	@login_required()
	def post(self):
		required_fields = [
			"exercise_id",
			"time",
			"keypresses"
		]
		for field in required_fields:
			if field not in request.json:
				abort(500)
		result = Result(exercise_id=request.json["exercise_id"],
						time=request.json["time"],
						keypresses=request.json["keypresses"],
						user_id=current_user_or_basic_auth().id)
		db.session.add(result)
		db.session.commit()
		_statistics = get_statistics(request.json["exercise_id"],
									 time=request.json["time"],
									 keypresses=request.json["keypresses"])
		return _statistics

api.add_resource(UserAPI, "/users/<id>")
api.add_resource(UserListAPI, "/users")
api.add_resource(ExerciseListAPI, "/exercises")
api.add_resource(ExerciseAPI, "/exercises/<id>")
api.add_resource(ResultsListAPI, "/results")
api.add_resource(ResultsAPI, "/results/<id>")



########################################### Paypal Check 1 #######################################################

@app.route('/success/')
def success():
	try:
		return render_template("success.html")
	except Exception, e:
		return(str(e))


@app.route('/ipn/',methods=['POST'])
def ipn():
	try:
		arg = ''
		request.parameter_storage_class = ImmutableOrderedMultiDict
		values = request.form
		for x, y in values.iteritems():
			arg += "&{x}={y}".format(x=x,y=y)

		validate_url = 'https://www.sandbox.paypal.com' \
					   '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
					   .format(arg=arg)
		r = requests.get(validate_url)
		if r.text == 'VERIFIED':
			try:
				payer_email =  thwart(request.form.get('payer_email'))
				unix = int(time.time())
				payment_date = thwart(request.form.get('payment_date'))
				username = thwart(request.form.get('custom'))
				last_name = thwart(request.form.get('last_name'))
				payment_gross = thwart(request.form.get('payment_gross'))
				payment_fee = thwart(request.form.get('payment_fee'))
				payment_net = float(payment_gross) - float(payment_fee)
				payment_status = thwart(request.form.get('payment_status'))
				txn_id = thwart(request.form.get('txn_id'))
			except Exception as e:
				with open('/tmp/ipnout.txt','a') as f:
					data = 'ERROR WITH IPN DATA\n'+str(values)+'\n'
					f.write(data)
			
			with open('/tmp/ipnout.txt','a') as f:
				data = 'SUCCESS\n'+str(values)+'\n'
				f.write(data)

		else:
			 with open('/tmp/ipnout.txt','a') as f:
				data = 'FAILURE\n'+str(values)+'\n'
				f.write(data)
				
		return r.text
	except Exception as e:
		return str(e)
#################################

##################
# Web App Routes #
##################

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		matches = User.query.filter_by(
			username=request.form.get("username", ""),
			password=request.form.get("password", "")).all()
		if len(matches) > 0:
			login_user(matches[0])
			return redirect(url_for('index'))
		flash('Username and/or password incorrect')
	hosttoserve = str(request.host)
	return render_template('login.html',**locals())

@app.route("/")
def index():
	if not current_user.is_authenticated:
		return redirect(url_for("login"))
	return render_template("index.html", **{"username": current_user.username})

@app.route("/results.html")
def results():
	if not current_user.is_authenticated:
		return redirect(url_for("login"))
	return render_template("results.html", **{"username": current_user.username})

@app.route("/logout")
@login_required()
def logout():
	logout_user()
	return redirect(url_for("index"))

def get_statistics(exercise_id, time, keypresses):
	results = Result.query.filter_by(exercise_id=exercise_id)
	times = np.array([result.time for result in results])
	_keypresses = np.array([result.keypresses for result in results])
	ret = {
		"times": sorted(map(int, times)),
		"keypresses": sorted(map(int, _keypresses)),
		"avg_time": float(np.mean(times)),
		"avg_keypresses": float(np.mean(_keypresses)),
		"max_time": float(np.amax(times)),
		"min_time": float(np.amin(times)),
		"median_time": float(np.median(times)),
		"max_keypresses": float(np.amax(_keypresses)),
		"min_keypresses": float(np.amin(_keypresses)),
		"median_keypresses": float(np.median(_keypresses)),
		"percentile_of_time": float(stats.percentileofscore(times, time)),
		"percentile_of_keypresses": float(stats.percentileofscore(_keypresses, keypresses)),
		"your_time": float(time),
		"your_keypresses": float(keypresses)
	}
	return jsonify(ret)

if __name__ == "__main__":
	manager.run()
