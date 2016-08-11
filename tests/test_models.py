from flask_testing import TestCase
from coding_scales import (app,
                           db,
                           User,
                           Exercise,
                           Collection,
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
        user_1 = User(username="test-user-1", password="test-pass")
        user_2 = User(username="test-user-2", password="test-pass")
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_users_exists(self):
        usernames = (user.username for user in User.query.all())
        self.assertIn("test-user-1", usernames)
        self.assertIn("test-user-2", usernames)
