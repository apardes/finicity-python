import random
import unittest
from collections import OrderedDict

import datetime

from .exceptions import ObjectDoesNotExist
from .resources import Customer, Institution, LoginField, MFAChallenge, Account
from . import Finicity


class FinicityTest(unittest.TestCase):
    def setUp(self):
        self.finicity = Finicity("2445581458544",
                                 "yEWtsRMzttEe3p8aD2xO",
                                 "ef7fc92a248c10fe0518a1da2cd4d84d")

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

    # def test_get_customers(self):
    #     self.finicity.authenticate()
    #
    #     customers = self.finicity.get_customers(dict())
    #     print [c.id for c in customers]

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


    # def test_get_accounts_without_mfa(self):
    #     self.finicity.authenticate()
    #
    #     customer_id = 5927425
    #     institution_id = 101732
    #     credentials = ["demo", "go"]
    #
    #     login_form = self.finicity.get_login_form(institution_id)
    #
    #     self.assertEqual(len(login_form), 2)
    #     self.assertEqual(login_form[0].name, "Banking Userid")
    #     self.assertEqual(login_form[1].name, "Banking Password")
    #
    #     _credentials = []
    #     for idx, field in enumerate(login_form):
    #         _credentials.append(dict(id=field.id,
    #                                  name=field.name,
    #                                  value=credentials[idx]))
    #     credentials = {
    #         "accounts": {
    #             "credentials": {
    #                 "loginField": _credentials
    #             }
    #         }
    #     }
    #
    #     accounts = self.finicity.get_accounts(customer_id, institution_id, credentials)
    #     self.assertIsInstance(accounts, list)
    #
    #     print [a.__dict__ for a in accounts]
    #     # chequing_account = [a for a in accounts if a.name == "Checking"][0]
    #     # print chequing_account.__dict__
    #
    #
    # def test_get_account_with_text_mfa(self):
    #     self.finicity.authenticate()
    #
    #     customer_id = 5927425
    #     institution_id = 101732
    #     credentials = ["tfa_text", "go"]
    #     answers = ["PET_NAME"]
    #
    #     login_form = self.finicity.get_login_form(institution_id)
    #
    #     self.assertEqual(len(login_form), 2)
    #     self.assertEqual(login_form[0].name, "Banking Userid")
    #     self.assertEqual(login_form[1].name, "Banking Password")
    #
    #     _credentials = []
    #     for idx, field in enumerate(login_form):
    #         _credentials.append(dict(id=field.id,
    #                                  name=field.name,
    #                                  value=credentials[idx]))
    #     credentials = {
    #         "accounts": {
    #             "credentials": {
    #                 "loginField": _credentials
    #             }
    #         }
    #     }
    #
    #     challenge = self.finicity.get_accounts(customer_id, institution_id, credentials)
    #
    #     self.assertIsInstance(challenge, MFAChallenge)
    #     self.assertEqual(len(challenge.questions), 1)
    #
    #     _answers = []
    #     for idx, question in enumerate(challenge.questions):
    #         _answers.append(dict(text=question.text,
    #                              answer=answers[idx]))
    #     mfa_response_data = {
    #         "accounts": {
    #             "mfaChallenges": {
    #                 "questions": {
    #                     "question": _answers
    #                 }
    #             }
    #         }
    #     }
    #
    #     accounts = self.finicity.mfa_response(customer_id,
    #                                           institution_id,
    #                                           challenge.session,
    #                                           mfa_response_data)
    #     self.assertIsInstance(accounts, list)
    #     self.assertGreater(len(accounts), 0)
    #     self.assertIsInstance(accounts[0], Account)
    #
    #     print [a.__dict__ for a in accounts]
    #
    # # TODO: Write tests for other MFA challenges

    def test_get_account_transactions(self):
        self.finicity.authenticate()

        # [u'5855823', u'5927410', u'5927425']
        # [8871545, 8871547, 8871548, 8871549, 8871551, 8871552]
        customer_id = 5927425
        account_id = 8871549
        from_date = int(datetime.datetime(2016, 1, 1, 0, 0, 0).strftime('%s'))
        to_date = int(datetime.datetime(2016, 5, 23, 23, 59, 59).strftime('%s'))


        query = dict(fromDate=from_date,
                     toDate=to_date)

        transactions = self.finicity.get_transactions(customer_id, account_id, query)
        print transactions.content
    #
    # def test_activate_accounts(self):
    #     self.finicity.authenticate()
    #
    #     customer_id = 5927425
    #     institution_id = 101732
    #     query = {
    #         "accounts": {
    #             "account": [
    #                 {
    #                     "id": 8871597,
    #                     "name": "Checking",
    #                     "type": "checking",
    #                     "number": 1000001111,
    #                     "status": "pending",
    #                 }
    #             ]
    #         }
    #     }
    #
    #     accounts = self.finicity.activate_accounts(customer_id, institution_id, query)
    #     print accounts


    # def test_refresh_account(self):
    #     """
    #     {u'status': u'active', u'name': u'Checking', u'institutionId': u'101732',
    #     u'number': u'1000001111', u'id': u'8871549', u'createdDate': u'1464050351',
    #     u'balance': u'523.27', u'type': u'checking', u'customerId': u'5927425'}
    #     """
    #     self.finicity.authenticate()
    #
    #     customer_id = 5927425
    #     account_id = 8871549
    #     query = {
    #         "accounts": {
    #             "account": [
    #                 {
    #                     "id": account_id,
    #                     "name": "Checking",
    #                     "type": "checking",
    #                     "number": "1000001111",
    #                     "status": "active",
    #                 }
    #             ]
    #         }
    #     }
    #
    #     accounts = self.finicity.refresh_account(customer_id, account_id, query)
    #     print accounts





