import random
import unittest
from collections import OrderedDict

from .exceptions import ObjectDoesNotExist
from .resources import Customer, Institution, LoginField
from . import Finicity

class FinicityTest(unittest.TestCase):
    def setUp(self):
        self.finicity = Finicity("",
                                 "",
                                 "")

    # def test_authenticate(self):
    #     self.finicity.authenticate()
    #     self.assertIsNotNone(self.finicity.app_token)
    #
    # def test_get_institutions(self):
    #     self.finicity.authenticate()
    #     self.assertIsNotNone(self.finicity.app_token)
    #
    #     institutions = self.finicity.get_institutions("finbank")
    #     self.assertGreater(len(institutions), 0)
    #
    # def test_get_institution(self):
    #     self.finicity.authenticate()
    #     self.assertIsNotNone(self.finicity.app_token)
    #
    #     institution = self.finicity.get_institution(101732)
    #     self.assertIsInstance(institution, Institution)
    #     self.assertEqual(institution.name, "FinBank")
    #
    # def test_add_testing_customer(self):
    #     self.finicity.authenticate()
    #     self.assertIsNotNone(self.finicity.app_token)
    #
    #     _customer = Customer(username="ellieharrison101", # +str(random.randint(1,1000)),
    #                          firstName="Ellie",
    #                          lastName="Harrison")
    #
    #     customer = self.finicity.add_testing_customer(_customer)
    #     self.assertIsInstance(customer, Customer)
    #     self.assertIsNotNone(customer.id)
    #     self.assertIsNotNone(customer.createdDate)
    #     self.assertEqual(customer.type, "testing")
    #
    # def test_get_customer(self):
    #     self.finicity.authenticate()
    #     self.assertIsNotNone(self.finicity.app_token)
    #
    #     customer = self.finicity.get_customer(5927425)
    #     self.assertIsInstance(customer, Customer)
    #     self.assertEqual(customer.username, "ellieharrison351")
    #     self.assertEqual(customer.firstName, "Ellie")
    #     self.assertEqual(customer.lastName, "Harrison")
    #
    #     with self.assertRaises(ObjectDoesNotExist):
    #         self.finicity.get_customer(1)
    #
    # def test_delete_customer(self):
    #     self.finicity.authenticate()
    #     self.assertIsNotNone(self.finicity.app_token)
    #
    #     customer = self.finicity.get_customers(dict(search="Ellie"))[0]
    #     customer_id = customer.id
    #
    #     self.assertTrue(self.finicity.delete_customer(customer_id))
    #     with self.assertRaises(ObjectDoesNotExist):
    #         self.finicity.get_customer(customer_id)


    def test_get_accounts(self):
        # self.finicity.authenticate()
        # self.assertIsNotNone(self.finicity.app_token)

        customer_id = 5927425
        institution_id = 101732
        credentials = dict(username="demo", password="go")

        # login_form = self.finicity.get_login_form(institution_id)
        # print([f.__dict__ for f in login_form])

        a = [OrderedDict([(u'id', u'101732001'), (u'name', u'Banking Userid'), (u'value', None), (u'description', u'Banking Userid'), (u'displayOrder', u'1'), (u'mask', u'false'), (u'instructions', None)]), OrderedDict([(u'id', u'101732002'), (u'name', u'Banking Password'), (u'value', None), (u'description', u'Banking Password'), (u'displayOrder', u'2'), (u'mask', u'true'), (u'instructions', None)])]
        form = LoginField(**a[0])

        # TODO: Write tests for login
        print(form.__dict__)


        #
        # print(self.finicity.get_accounts(customer_id,
        #                                  institution_id,
        #                                  credentials))










