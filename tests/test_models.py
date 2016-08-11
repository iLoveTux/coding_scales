from flask_testing import TestCase
from coding_scales import (app,
                           db,
                           User,
                           Exercise,
                           Result,
                           configure_app)

class TestModels(TestCase):
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

    def test_users_exists(self):
        usernames = (user.username for user in User.query.all())
        self.assertIn("test-user-1", usernames)
        self.assertIn("test-user-2", usernames)

    def test_find_user_by_email(self):
        user = User.query.filter_by(email="1@test.com").all()
        self.assertEqual(len(user), 1)

    def test_find_users_exercises(self):
        user = User.query.filter_by(email="1@test.com").first()
        expected = Exercise.query.filter_by(author_id=user.id).all()
        results = user.exercises.all()
        self.assertEqual(expected, results)

    def test_user_has_expected_columns(self):
        """Kind of like documentation for columns in user
        """
        user = User.query.first()
        assert hasattr(user, "id")
        assert hasattr(user, "username")
        assert hasattr(user, "password")
        assert hasattr(user, "email")
        assert hasattr(user, "date_joined")
        assert hasattr(user, "billing_date")
        assert hasattr(user, "verified")
        assert hasattr(user, "role")
        assert hasattr(user, "exercises")
        assert hasattr(user, "results")

    def test_exercise_has_expected_columns(self):
        """Kind of like documentation for columns in user
        """
        exercise = Exercise.query.first()
        assert hasattr(exercise, "author_id")
        assert hasattr(exercise, "author")
        assert hasattr(exercise, "text")
        assert hasattr(exercise, "name")
        assert hasattr(exercise, "date_added")
        assert hasattr(exercise, "language")
        assert hasattr(exercise, "results")

    def test_result_has_expected_columns(self):
        """Kind of like documentation for columns in user
        """
        result = Result.query.first()
        assert hasattr(result, "user_id")
        assert hasattr(result, "exercise_id")
        assert hasattr(result, "time")
        assert hasattr(result, "date")
        assert hasattr(result, "user")
        assert hasattr(result, "exercise")

    def test_language_is_lowercase(self):
        """This constraint is to reduce redundant language tags
        The test exercises added to the db use different case
        for the "p" in python.
        """
        languages = set([e.language for e in Exercise.query.all()])
        self.assertEqual(list(languages), ["python"])
