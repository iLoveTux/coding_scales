from flask_testing import TestCase
from flask import request, session
import json
from flask_restful import marshal
from coding_scales import (app,
                           db,
                           User,
                           Exercise,
                           Result,
                           user_fields)

class TestAPI(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    def create_app(self):
        return app

    def setUp(self):
        db.drop_all()
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
        db.session.add(exercise_3)
        db.session.commit()
        db.session.add_all([Result(user_id=user_1.id,
                                   exercise_id=exercise_1.id,
                                   time=2,
                                   keypresses=14),
                            Result(user_id=user_2.id,
                                   exercise_id=exercise_2.id,
                                   time=2,
                                   keypresses=14),
                            Result(user_id=admin.id,
                                   exercise_id=exercise_3.id,
                                   time=2,
                                   keypresses=14)])
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
        """Ensure that a GET request for "/users" returns a JSON
        object which includes all registered users.
        """
        self.login("test-user-1", "test-pass")
        results = self.client.get("/users").json
        expected = User.query.all()
        expected = marshal(expected, user_fields)
        self.assertEqual(expected, results)

    def test_get_user(self):
        """Ensure that a GET request for "/users/<id>" returns
        a JSON object detailing the user.
        """
        pass

    def test_admin_can_alter_user(self):
        """Given an admin user they should be able to update any
        users attributes
        """
        pass

    def test_user_cannot_update_another_users_profile(self):
        """A user should not be able to update another users' profile
        """
        pass

    def test_user_can_update_own_profiles(self):
        """A user should be able to update their own profile
        """
        pass

    def test_user_can_create_exercise(self):
        """A user should be able to create exercises for themselves
        and others to use.
        """
        pass
    def test_user_cannot_create_exercises_for_other_users(self):
        """An exercise created by one user should not be able to
        be attributed to another user
        """
        pass

    def test_user_can_post_results(self):
        """A user should be able to post the results of their performance
        on a particular exercise.
        """
        pass

    def test_user_cannot_post_results_for_others(self):
        """A user should not be able to post results on behalf of others
        """
        pass

