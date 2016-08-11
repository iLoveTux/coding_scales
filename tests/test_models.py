from unittest import TestCase

class TestModels(TestCase):
    def test_models_exist(self):
        from coding_scales import models
        self.assertIn("User", models.__dict__.keys())
        self.assertIn("Exercise", models.__dict__.keys())
        self.assertIn("Collection", models.__dict__.keys())
