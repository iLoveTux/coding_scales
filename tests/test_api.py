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

    def setUp(self):
        db.create_all()
        user_1 = User(username="test-user-1",
                      password="test-pass",
                      email="1@test.com")
        user_2 = User(username="test-user-2",
                      password="test-pass",
                      email="2@test.com")
        admin = User(username="admin",
                     password="admin",
                     email="admin@test.com")
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.add(admin)
        db.session.commit()
        exercise_1 = Exercise(author_id=user_1.id,
                              text='print("hello, world!")\n',
                              language="python",
                              name="user-1-hello-world")
        exercise_2 = Exercise(author_id=user_2.id,
                              text='print("hello, world!")\n',
                              language="Python",
                              name="user-2-hello-world")
        exercise_3 = Exercise(author_id=admin.id,
                              text='print("hello, world!")\n',
                              language="Python",
                              name="admin-hello-world")
        db.session.add(exercise_1)
        db.session.add(exercise_2)
        db.session.commit()
        db.session.add_all([Result(user_id=user_1.id,
                                   exercise_id=exercise_1.id,
                                   time=2),
                            Result(user_id=user_2.id,
                                   exercise_id=exercise_2.id,
                                   time=2),
                            Result(user_id=admin.id,
                                   exercise_id=exercise_3.id,
                                   time=2)])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, username, password):
        return self.client.post("/login",
                                data={
                                   "username": username,
                                   "password": password
                                },
                                follow_redirects=True)

    def logout(self):
        return self.client.get("/logout", follow_redirects=True)

    def test_get_users(self):
        self.login("test-user-1", "test-pass")
        results = self.client.get("/users").json
        expected = {"users": ["http://localhost:5000/users/1",
                              "http://localhost:5000/users/2",
                              "http://localhost:5000/users/3"]}
        self.assertEqual(expected, results)
