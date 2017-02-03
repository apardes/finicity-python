from xmltodict import parse, unparse

from finicity.exceptions import ObjectDoesNotExist, MissingParameter
from .utils import endpoint
from .compat import cache
from .http import Requester
from .resources import Institution, LoginField, Customer, Account, BaseMFA, MFAChallenge, Transaction


class Finicity(object):
    CACHE_KEY = "FINICITY_TOKEN"
    TOKEN_EXPIRY = 90 * 60  # Seconds

    def __init__(self, partner_id, partner_secret, app_key):
        self.partner_id = partner_id
        self.partner_secret = partner_secret
        self.app_key = app_key
        self.app_token = None
        self.http = Requester("https://api.finicity.com/aggregation/", app_key)

    def handle_mfa_response(self, response):
        mfa_response_data = parse(response.content)
        mfa_questions = []
        questions = mfa_response_data["mfaChallenges"]["questions"]["question"]
        if not isinstance(questions, list):
            questions = [questions]

        for question in questions:
            mfa_questions.append(BaseMFA.deserialize(question))
        mfa_challenge = MFAChallenge(session=response.headers.get("MFA-Session"),
                                     questions=mfa_questions)
        return mfa_challenge

    @endpoint("POST", "v2/partners/authentication", token_required=False)
    def authenticate(self, *args, **kwargs):
        token = cache.get(self.CACHE_KEY)
        if token is not None:
            self.app_token = token
            return token

        body = dict(credentials=dict(partnerId=self.partner_id,
                                     partnerSecret=self.partner_secret))
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'],
                                     body)

        try:
            content = parse(response.content)
        except:
            print (response.content)
            raise MissingParameter("Finicity Authentication Error")
        token = content['access']['token']
        cache.set(self.CACHE_KEY, token, self.TOKEN_EXPIRY)
        self.app_token = token
        return token

    @endpoint("GET", "v1/institutions")
    def get_institutions(self, name=None, *args, **kwargs):

        if not name:
            name = "*"

        body = dict(search=name.strip())
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'],
                                     body,
                                     headers={'Finicity-App-Token': self.app_token})

        institutions = parse(response.content)

        if int(institutions['institutions']['@found']) == 1:
            institutions = [institutions['institutions']['institution']]
        elif int(institutions['institutions']['@found']) > 1:
            institutions = [ins for ins in institutions['institutions']['institution']]
        else:
            institutions = []
        return [Institution(**ins) for ins in institutions]

    @endpoint("GET", "v1/institutions/{institution_id}")
    def get_institution(self, institution_id, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(institution_id=institution_id),
                                     headers={'Finicity-App-Token': self.app_token})
        parsed_response = parse(response.content)
        if 'institution' in parsed_response:
            return Institution(**parsed_response['institution'])
        raise ObjectDoesNotExist("Institution with id {} does not exist".format(institution_id))

    @endpoint("GET", "v1/institutions/{institution_id}/loginForm")
    def get_login_form(self, institution_id, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(institution_id=institution_id),
                                     headers={'Finicity-App-Token': self.app_token})
        fields = parse(response.content).get('loginForm', [])

        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            http_status = response.status_code
            response = parse(response.content)
            raise MissingParameter('HTTP Error: {}, Finicity Error {}: {}'.format(http_status, response['error']['message'], response['error']['code']))


        return [LoginField(**field) for field in fields['loginField']]

    def parse_login_field(self, login_form, css=None):
        parsed_form = list()
        for login_field  in login_form:
            parsed_field = dict()

            parsed_field['label'] = login_field.description
            parsed_field['id'] = login_field.id
            parsed_field['display_order'] = login_field.displayOrder
            parsed_field['name'] = login_field.name
            parsed_field['mask'] = login_field.mask


            if not css:
                css = ""

            if login_field.mask == "true":
                html_input = '<input type="password" id="fi-pass" class="{}" data-input-id="{}" data-input-name="{}">'.format(css, login_field.id, login_field.name)
                pass_dup_input = '<input type="password" id="fi-pass-dup" class="{}" data-input-id="{}" data-input-name="{}" data-nullify="1">'.format(css, login_field.id, login_field.name)
            else:
                html_input = '<input type="text" class="{}" data-input-id="{}" data-input-name="{}">'.format(css, login_field.id, login_field.name)

            if login_field.mask == "true":
                pass_dup_field = dict(parsed_field)
                pass_dup_field['html_input'] = pass_dup_input
                pass_dup_field['label'] = "Confirm " + pass_dup_field['label']
                pass_dup_field['display_order'] = str(int(pass_dup_field['display_order']) + 1)
                parsed_form.append(pass_dup_field)

            parsed_field['html_input'] = html_input

            parsed_form.append(parsed_field)

        return parsed_form


    @endpoint("POST", "v1/customers/testing")
    def add_testing_customer(self, customer, *args, **kwargs):
        assert isinstance(customer, Customer)
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'],
                                     body=dict(customer=customer.__dict__),
                                     headers={'Finicity-App-Token': self.app_token})
        _customer = parse(response.content)
        try:
            customer.id = _customer['customer']['id']
            customer.createdDate = _customer['customer']['createdDate']
        except:
            print ("Failed to create customer")
            print (_customer)
            return None
        else:
            customer.type = "testing"
            return customer


    @endpoint("POST", "v1/customers/active")
    def add_customer(self, customer, *args, **kwargs):
        assert isinstance(customer, Customer)
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'],
                                     body=dict(customer=customer.__dict__),
                                     headers={'Finicity-App-Token': self.app_token})
        _customer = parse(response.content)
        try:
            customer.id = _customer['customer']['id']
            customer.createdDate = _customer['customer']['createdDate']
        except:
            print ("Failed to create customer")
            print (_customer)
            return None
        else:
            customer.type = "active"
            return customer


    @endpoint("GET", "v1/customers")
    def get_customers(self, querystring, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'],
                                     body=querystring,
                                     headers={'Finicity-App-Token': self.app_token})
        customers = parse(response.content)
        if int(customers['customers']['@displaying']) == 1:
            customers = [customers['customers']['customer']]
        elif int(customers['customers']['@displaying']) > 1:
            customers = [cus for cus in customers['customers']['customer']]
        else:
            customers = []
        return [Customer(**cus) for cus in customers]

    @endpoint("GET", "v1/customers/{customer_id}")
    def get_customer(self, customer_id, *args, **kwargs):
        response = self.http.request(kwargsf['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id),
                                     headers={'Finicity-App-Token': self.app_token})
        parsed_response = parse(response.content)
        if 'customer' in parsed_response:
            return Customer(**parsed_response['customer'])
        raise ObjectDoesNotExist("Customer with id {} does not exist".format(customer_id))

    @endpoint("DELETE", "v1/customers/{customer_id}")
    def delete_customer(self, customer_id, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id),
                                     headers={'Finicity-App-Token': self.app_token})
        return response.status_code == 204

    @endpoint("POST", "v1/customers/{customer_id}/institutions/{institution_id}/accounts/addall")
    def add_all_accounts(self, customer_id, institution_id, body, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    institution_id=institution_id),
                                     body=body,
                                     headers={'Finicity-App-Token': self.app_token})

        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            http_status = response.status_code
            response = parse(response.content)
            raise MissingParameter('HTTP Error: {}, Finicity Error {}: {}'.format(http_status, response['error']['message'], response['error']['code']))

        print (response.content)

        accounts = parse(response.content).get('accounts', [])

        print (accounts)

        if not isinstance(accounts['account'], list):
            questions = [accounts['account']]


        accounts = [Account.deserialize(account) for account in accounts['account']]

        print (accounts)

        return accounts

    @endpoint("POST", "v1/customers/{customer_id}/institutions/{institution_id}/accounts")
    def get_accounts(self, customer_id, institution_id, body, *args, **kwargs):

        response = self.http.request(
                    kwargs['method'],
                    kwargs['endpoint_path'].format(customer_id=customer_id,
                    institution_id=institution_id),
                    body=body,
                    headers={'Finicity-App-Token': self.app_token},
                )

        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            http_status = response.status_code
            response = parse(response.content)
            raise MissingParameter('HTTP Error: {}, Finicity Error {}: {}'.format(http_status, response['error']['message'], response['error']['code']))

        accounts = parse(response.content).get('accounts', [])

        return [Account.deserialize(account) for account in accounts['account']]

    @endpoint("POST", "v1/customers/{customer_id}/accounts")
    def refresh_customer_accounts(self, customer_id, body=None, *args, **kwargs):

        response = self.http.request(
                    kwargs['method'],
                    kwargs['endpoint_path'].format(customer_id=customer_id),
                    body=body,
                    headers={'Finicity-App-Token': self.app_token},
                )

        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            http_status = response.status_code
            response = parse(response.content)
            raise MissingParameter('HTTP Error: {}, Finicity Error {}: {}'.format(http_status, response['error']['message'], response['error']['code']))

        accounts = parse(response.content).get('accounts', [])

        return [Account.deserialize(account) for account in accounts['account']]


    @endpoint("GET", "v1/customers/{customer_id}/accounts")
    def get_all_customer_accounts(self, customer_id, body=None, *args, **kwargs):

        response = self.http.request(
                    kwargs['method'],
                    kwargs['endpoint_path'].format(customer_id=customer_id),
                    body=body,
                    headers={'Finicity-App-Token': self.app_token},
                )

        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            http_status = response.status_code
            response = parse(response.content)
            raise MissingParameter('HTTP Error: {}, Finicity Error {}: {}'.format(http_status, response['error']['message'], response['error']['code']))

        accounts = parse(response.content).get('accounts', [])

        return [Account.deserialize(account) for account in accounts['account']]


    @endpoint("GET", "v1/customers/{customer_id}/accounts/{account_id}")
    def get_account(self, customer_id, account_id, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    account_id=account_id),
                                     headers={'Finicity-App-Token': self.app_token})
        
        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            http_status = response.status_code
            response = parse(response.content)
            raise MissingParameter('HTTP Error: {}, Finicity Error {}: {}'.format(http_status, response['error']['message'], response['error']['code']))

        account = Account.deserialize(parse(response.content).get('account'))

        return account

    @endpoint("PUT", "v1/customers/{customer_id}/institutions/{institution_id}/accounts")
    def activate_accounts(self, customer_id, institution_id, body, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    institution_id=institution_id),
                                     body=body,
                                     headers={'Finicity-App-Token': self.app_token})
        if response.status_code == 203:
            return self.handle_mfa_response(response)
        accounts = parse(response.content).get('accounts', [])
        return [Account.deserialize(account) for account in accounts['account']]


    @endpoint("POST", 'v1/customers/{customer_id}/institutionLogins/{institution_login_id}/accounts')
    def refresh_institution_login(self, customer_id, institution_login_id, body=None, *args, **kwargs):
        response = self.http.request(
            kwargs['method'],
            kwargs['endpoint_path'].format(
                customer_id = customer_id,
                institution_login_id = institution_login_id),
            body = body,
            headers = {'Finicity-App-Token' : self.app_token}
        )

        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            print (response.content)
            response = parse(response.content)
            raise MissingParameter('HTTP Error: {}, Finicity Error {}: {}'.format(response.status_code, response['error']['message'], response['error']['code']))

        accounts = parse(response.content).get('accounts', [])
        return [Account.deserialize(account) for account in accounts['account']]


    ### Deprecated
    @endpoint("POST", "v1/customers/{customer_id}/accounts/{account_id}")
    def refresh_account(self, customer_id, account_id, body=None, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    account_id=account_id),
                                     body=body,
                                     headers={'Finicity-App-Token': self.app_token})
        if response.status_code == 203:
            return self.handle_mfa_response(response)

        accounts = parse(response.content).get('accounts', [])
        return [Account.deserialize(account) for account in accounts['account']]

    @endpoint("POST", "v1/customers/{customer_id}/institutions/{institution_id}/accounts/addall/mfa")
    def mfa_response(self, customer_id, institution_id, mfa_session, body, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    institution_id=institution_id),
                                     body=body,
                                     headers={'Finicity-App-Token': self.app_token,
                                              'MFA-Session': mfa_session})
        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code >= 400:
            print (response.content)
            try:
                raise MissingParameter('HTTP Error: {}, Finicity Error: {}: {}'.format(response.status_code, response['error']['message'], response['error']['code']))
            except:
                raise MissingParameter('Finicity Server Error')

        accounts = parse(response.content).get('accounts', [])
        return [Account.deserialize(account) for account in accounts['account']]


    @endpoint("POST", "v1/customers/{customer_id}/accounts/{account_id}/transactions/historic")
    def get_historic_transactions(self, customer_id, account_id, body=None, *args, **kwargs):

        response = self.http.request(
            kwargs['method'], 
            kwargs['endpoint_path'].format(customer_id = customer_id, account_id = account_id), 
            body = body,
            headers = {'Finicity-App-Token' : self.app_token}
        )

        if response.status_code == 203:
            return self.handle_mfa_response(response)
        elif response.status_code == 204:
            return True
        else:
            print (response.status_code)
            print (response.content)
            raise MissingParameter('Unable to load historic transactions')


    @endpoint("GET", "v2/customers/{customer_id}/accounts/{account_id}/transactions")
    def get_transactions(self, customer_id, account_id, body, *args, **kwargs):

        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    account_id=account_id),
                                     body=body,
                                     headers={'Finicity-App-Token': self.app_token})


        if response.status_code >= 400:
            print (response.content)
            return None, None
        else:
            response = parse(response.content)

            more_available = response['transactions']['@moreAvailable']
            
            if (more_available == "true") or (more_available == True):
                more_available = True
            else:
                more_available = False

            if response['transactions']['@displaying'] == "1":
                transactions = [response['transactions']['transaction']]
            else:
                transactions = response['transactions']['transaction']

            return [Transaction(**t) for t in transactions], more_available
