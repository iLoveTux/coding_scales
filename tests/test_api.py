from flask_testing import TestCase
from flask import request, session
import json
from coding_scales import (app,
                           db,
                           User,
                           Exercise,
                           Result,
                           configure_app)
class TestAPI(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        # pass in test configuration
        return configure_app(debug=True,
                             testing=True,
                             db_uri="sqlite://")

    def setUp(self):
        db.create_all()
        user_1 = User(username="test-user-1",
                      password="test-pass",
                      email="1@test.com")
        user_2 = User(username="test-user-2",
                      password="test-pass",
                      email="2@test.com")
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()
        exercise_1 = Exercise(author_id=user_1.id,
                              text='print("hello, world!")\n',
                              language="python",
                              name="user-1-hello-world")
        exercise_2 = Exercise(author_id=user_2.id,
                              text='print("hello, world!")\n',
                              language="Python",
                              name="user-2-hello-world")
        db.session.add(exercise_1)
        db.session.add(exercise_2)
        db.session.commit()
        db.session.add_all([Result(user_id=user_1.id,
                                   exercise_id=exercise_1.id,
                                   time=2),
                            Result(user_id=user_2.id,
                                   exercise_id=exercise_2.id,
                                   time=2)])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_get_users_returns_all_users(self):
        expected = ["test-user-1", "test-user-2"]
        resp = self.client.get("/api/users").json
        results = [user["username"] for user in resp["objects"]]
        self.assertEqual(expected, results)

    def test_get_exercises(self):
        expected = [e.name for e in User.query.filter_by(username="test-user-1").first().exercises]
        resp = self.client.get("/api/exercises").json
        results = [e["name"] for e in resp["objects"] if e["author"]["username"] == "test-user-1"]
        self.assertEqual(expected, results)

    def test_fields_returned_for_user(self):
        resp = self.client.get("/api/users").json
        user = resp["objects"][0]
        self.assertIn("id", user)
        self.assertIn("date_joined", user)
        self.assertIn("exercises", user)
        self.assertIn("results", user)
        self.assertNotIn("password", user)
        self.assertNotIn("verified", user)
        self.assertNotIn("billing_date", user)
        self.assertNotIn("role", user)

    def test_fields_returned_for_exercise(self):
        resp = self.client.get("/api/exercises").json
        exercise = resp["objects"][0]
        self.assertIn("id", exercise)
        self.assertIn("date_added", exercise)
        self.assertIn("language", exercise)
        self.assertIn("text", exercise)
        self.assertIn("author", exercise)
        self.assertIn("results", exercise)

    def test_fields_returned_for_results(self):
        resp = self.client.get("/api/results").json
        result = resp["objects"][0]
        self.assertIn("user", result)
        self.assertIn("exercise", result)
        self.assertIn("time", result)
        self.assertIn("date", result)

class TestRBM(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def login(self):
        pass

    def create_app(self):
        # pass in test configuration
        return configure_app(debug=True,
                             testing=True,
                             db_uri="sqlite://")

    def setUp(self):
        db.create_all()
        user_1 = User(username="test-user-1",
                      password="test-pass",
                      email="1@test.com")
        user_2 = User(username="test-user-2",
                      password="test-pass",
                      email="2@test.com")
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()
        exercise_1 = Exercise(author_id=user_1.id,
                              text='print("hello, world!")\n',
                              language="python",
                              name="user-1-hello-world")
        exercise_2 = Exercise(author_id=user_2.id,
                              text='print("hello, world!")\n',
                              language="Python",
                              name="user-2-hello-world")
        db.session.add(exercise_1)
        db.session.add(exercise_2)
        db.session.commit()
        db.session.add_all([Result(user_id=user_1.id,
                                   exercise_id=exercise_1.id,
                                   time=2),
                            Result(user_id=user_2.id,
                                   exercise_id=exercise_2.id,
                                   time=2)])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    # def test_access_control(self):
    #     user = User.query.filter_by(role="admin").first()
    #     print(request.session)
    #     self.client.request.user = user

