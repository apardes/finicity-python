import unittest
from . import Finicity

class FinicityTest(unittest.TestCase):
    def setUp(self):
        self.finicity = Finicity("2445581458544",
                                 "yEWtsRMzttEe3p8aD2xO",
                                 "ef7fc92a248c10fe0518a1da2cd4d84d")

    def test_authenticate(self):
        self.finicity.authenticate()
        self.assertIsNotNone(self.finicity.app_token)

    def test_get_institutions(self):
        self.finicity.authenticate()
        self.assertIsNotNone(self.finicity.app_token)

        institutions = self.finicity.get_institutions("finbank")
        self.assertGreater(len(institutions), 0)


