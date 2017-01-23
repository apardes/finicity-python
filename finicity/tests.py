import random
import unittest
from collections import OrderedDict

import datetime

from .exceptions import ObjectDoesNotExist
from .resources import Customer, Institution, LoginField, MFAChallenge, Account
from . import Finicity


finicity = Finicity("2445581458544",
                    "yEWtsRMzttEe3p8aD2xO",
                    "ef7fc92a248c10fe0518a1da2cd4d84d")


class FinicityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _customer = Customer(username="aprilsummers",
                             firstName="April",
                             lastName="Summers")
        finicity.authenticate()
        cls.customer = finicity.add_testing_customer(_customer)
        cls.accounts = None

    @classmethod
    def tearDownClass(cls):
        finicity.delete_customer(cls.customer.id)

    def setUp(self):
        self.finicity = finicity
        self.institution_id = 101732


    def test_authenticate(self):
        self.finicity.authenticate()
        self.assertIsNotNone(self.finicity.app_token)

    def test_get_institutions(self):
        self.finicity.authenticate()

        institutions = self.finicity.get_institutions("finbank")
        self.assertGreater(len(institutions), 0)

    def test_get_institution(self):
        self.finicity.authenticate()

        institution = self.finicity.get_institution(101732)
        self.assertIsInstance(institution, Institution)
        self.assertEqual(institution.name, "FinBank")

    def test_add_testing_customer(self):
        self.finicity.authenticate()

        _customer = Customer(username="ellieharrison101", # +str(random.randint(1,1000)),
                             firstName="Ellie",
                             lastName="Harrison")
        customer = self.finicity.add_testing_customer(_customer)
        self.assertIsInstance(customer, Customer)
        self.assertIsNotNone(customer.id)
        self.assertIsNotNone(customer.createdDate)
        self.assertEqual(customer.type, "testing")

    def test_get_customers(self):
        self.finicity.authenticate()

        customers = self.finicity.get_customers(dict())
        self.assertGreater(len(customers), 2)

    def test_get_customer(self):
        self.finicity.authenticate()

        customer = self.finicity.get_customer(self.customer.id)
        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.username, "aprilsummers")
        self.assertEqual(customer.firstName, "April")
        self.assertEqual(customer.lastName, "Summers")

        with self.assertRaises(ObjectDoesNotExist):
            self.finicity.get_customer(1)

    def test_delete_customer(self):
        self.finicity.authenticate()

        customer = self.finicity.get_customers(dict(username="ellieharrison101"))[0]
        customer_id = customer.id

        self.assertTrue(self.finicity.delete_customer(customer_id))
        with self.assertRaises(ObjectDoesNotExist):
            self.finicity.get_customer(customer_id)

    def test_get_accounts_without_mfa(self):
        self.finicity.authenticate()

        customer_id = FinicityTest.customer.id
        institution_id = self.institution_id
        credentials = ["demo", "go"]

        login_form = self.finicity.get_login_form(institution_id)

        self.assertEqual(len(login_form), 2)
        self.assertEqual(login_form[0].name, "Banking Userid")
        self.assertEqual(login_form[1].name, "Banking Password")

        _credentials = []
        for idx, field in enumerate(login_form):
            _credentials.append(dict(id=field.id,
                                     name=field.name,
                                     value=credentials[idx]))
        credentials = {
            "accounts": {
                "credentials": {
                    "loginField": _credentials
                }
            }
        }

        accounts = self.finicity.get_accounts(customer_id, institution_id, credentials)
        self.assertIsInstance(accounts, list)
        self.assertIsInstance(accounts[0], Account)

    def test_get_account_with_text_mfa(self):
        self.finicity.authenticate()

        customer_id = FinicityTest.customer.id
        institution_id = self.institution_id
        credentials = ["tfa_text", "go"]
        answers = ["PET_NAME"]

        login_form = self.finicity.get_login_form(institution_id)

        self.assertEqual(len(login_form), 2)
        self.assertEqual(login_form[0].name, "Banking Userid")
        self.assertEqual(login_form[1].name, "Banking Password")

        _credentials = []
        for idx, field in enumerate(login_form):
            _credentials.append(dict(id=field.id,
                                     name=field.name,
                                     value=credentials[idx]))
        credentials = {
            "accounts": {
                "credentials": {
                    "loginField": _credentials
                }
            }
        }

        challenge = self.finicity.get_accounts(customer_id, institution_id, credentials)

        self.assertIsInstance(challenge, MFAChallenge)
        self.assertEqual(len(challenge.questions), 1)

        _answers = []
        for idx, question in enumerate(challenge.questions):
            _answers.append(dict(text=question.text,
                                 answer=answers[idx]))
        mfa_response_data = {
            "accounts": {
                "mfaChallenges": {
                    "questions": {
                        "question": _answers
                    }
                }
            }
        }

        accounts = self.finicity.mfa_response(customer_id,
                                              institution_id,
                                              challenge.session,
                                              mfa_response_data)
        self.assertIsInstance(accounts, list)
        self.assertGreater(len(accounts), 0)
        self.assertIsInstance(accounts[0], Account)

        FinicityTest.accounts = accounts

    # TODO: Write tests for other MFA challenges

    # def test_activate_accounts(self):
    #     self.finicity.authenticate()
    #
    #     customer_id = FinicityTest.customer.id
    #     institution_id = self.institution_id
    #     answers = ["PET_NAME"]
    #
    #     accounts = self.finicity.get_accounts(customer_id, institution_id)
    #
    #
    #     creditcard_account = [a for a in FinicityTest.accounts if a.type == "creditcard"][0]
    #
    #     query = {
    #         "accounts": {
    #             "account": [
    #                 {
    #                     "id": creditcard_account.id,
    #                     "type": "creditcard",
    #                     "number": creditcard_account.number,
    #                     "status": "active",
    #                 }
    #             ]
    #         }
    #     }
    #
    #     response = self.finicity.activate_accounts(customer_id, institution_id, query)
    #
    #     if isinstance(response, MFAChallenge):
    #         challenge = response
    #
    #         self.assertIsInstance(challenge, MFAChallenge)
    #         self.assertEqual(len(challenge.questions), 1)
    #
    #         _answers = []
    #         for idx, question in enumerate(challenge.questions):
    #             _answers.append(dict(text=question.text,
    #                                  answer=answers[idx]))
    #         mfa_response_data = {
    #             "accounts": {
    #                 "mfaChallenges": {
    #                     "questions": {
    #                         "question": _answers
    #                     }
    #                 }
    #             }
    #         }
    #
    #         accounts = self.finicity.mfa_response(customer_id,
    #                                               institution_id,
    #                                               challenge.session,
    #                                               mfa_response_data)
    #         self.assertIsInstance(accounts, list)
    #         self.assertGreater(len(accounts), 0)
    #         self.assertIsInstance(accounts[0], Account)
    #
    #         print([a.__dict__ for a in accounts])
    #
    #     print(response)

    # def test_refresh_account(self):
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


    def test_get_account_transactions(self):
        self.finicity.authenticate()

        # [u'5855823', u'5927410', u'5927425']
        # [8871545, 8871547, 8871548, 8871549, 8871551, 8871552]

        # {'_BaseObject__required_fields': [], u'status': u'active', u'name': u'Checking', '_BaseObject__optional_fields': [], u'balance': u'524.02', u'type': u'checking', u'number': u'1000001111', u'id': u'8871597'}
        customer_id = 5927425
        account_id = 8871597
        from_date = int(datetime.datetime(2016, 1, 1, 0, 0, 0).strftime('%s'))
        to_date = int(datetime.datetime(2016, 5, 23, 23, 59, 59).strftime('%s'))


        query = dict(fromDate=from_date,
                     toDate=to_date)

        transactions = self.finicity.get_transactions(customer_id, account_id, query)
        print (transactions)



