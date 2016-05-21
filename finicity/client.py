from xmltodict import parse, unparse
from .utils import endpoint
from .compat import cache
from .http import Requester
from .resources import Institution, LoginField, Customer, Account, BaseMFA, MFAChallenge


class Finicity(object):
    CACHE_KEY = "FINICITY_TOKEN"
    TOKEN_EXPIRY = 10  # Seconds

    def __init__(self, partner_id, partner_secret, app_key):
        self.partner_id = partner_id
        self.partner_secret = partner_secret
        self.app_key = app_key
        self.app_token = None
        self.http = Requester("https://api.finicity.com/aggregation/", app_key, debug=True)

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
        content = parse(response.content)
        token = content['access']['token']
        cache.set(self.CACHE_KEY, token, self.TOKEN_EXPIRY)
        self.app_token = token
        return token

    @endpoint("GET", "v1/institutions")
    def get_institutions(self, name, *args, **kwargs):
        if len(name) < 3:
            return []

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
        return Institution(**parse(response.content)['institution'])

    @endpoint("GET", "v1/institutions/{institution_id}/loginForm")
    def get_login_form(self, institution_id, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(institution_id=institution_id),
                                     headers={'Finicity-App-Token': self.app_token})
        fields = parse(response.content).get('loginForm', [])
        return [LoginField(**field) for field in fields['loginField']]

    @endpoint("POST", "v1/customers/testing")
    def add_testing_customer(self, customer, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'],
                                     body=customer,
                                     headers={'Finicity-App-Token': self.app_token})
        return parse(response.content)

    @endpoint("GET", "v1/customers/{customer_id}")
    def get_customer(self, customer_id, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id),
                                     headers={'Finicity-App-Token': self.app_token})
        return Customer(**parse(response.content)['customer'])

    @endpoint("POST", "v1/customers/{customer_id}/institutions/{institution_id}/accounts/addall")
    def add_all_accounts(self, customer_id, institution_id, body, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    institution_id=institution_id),
                                     body=body,
                                     headers={'Finicity-App-Token': self.app_token})
        if response.status_code == 203:
            return self.handle_mfa_response(response)

        accounts = parse(response.content).get('accounts', [])
        return [Account.deserialize(account) for account in accounts['account']]

    @endpoint("GET", "v1/customers/{customer_id}/accounts/{account_id}")
    def get_account(self, customer_id, account_id, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    account_id=account_id),
                                     headers={'Finicity-App-Token': self.app_token})
        return response

    @endpoint("POST", "v1/customers/{customer_id}/institutions/{institution_id}/accounts/addall/mfa")
    def mfa_response(self, customer_id, institution_id, mfa_session, body, *args, **kwargs):
        response = self.http.request(kwargs['method'],
                                     kwargs['endpoint_path'].format(customer_id=customer_id,
                                                                    institution_id=institution_id),
                                     body=body,
                                     headers={'Finicity-App-Token': self.app_token,
                                              'MFA-Session': mfa_session})
        if response.status_code == 203:
            self.handle_mfa_response(response)

        accounts = parse(response.content).get('accounts', [])
        return [Account.deserialize(account) for account in accounts['account']]
