from flask_testing import TestCase
import json
from coding_scales import (app,
                           db,
                           User,
                           Exercise,
                           Result,
                           configure_app)
class TestUserAPI(TestCase):
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
