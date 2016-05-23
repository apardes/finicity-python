from .utils import enum

class BaseObject(object):
    # required_fields = []
    # optional_fields = []

    def __init__(self, **kwargs):
        self.__required_fields = []
        self.__optional_fields = []

        for key, value in kwargs.items():
            if key in self.optional_fields \
                    or key in self.required_fields:
                self.__dict__.update({key: value})

    @property
    def required_fields(self):
        return self.__required_fields

    @required_fields.setter
    def required_fields(self, value):
        self.__required_fields = value

    @property
    def optional_fields(self):
        return self.__optional_fields

    @optional_fields.setter
    def optional_fields(self, value):
        self.__optional_fields = value


class BaseResource(BaseObject):
    def __init__(self, *args, **kwargs):
        missing_fields = []
        for field in self.required_fields:
            if field not in kwargs:
                missing_fields.append(field)
        if len(missing_fields) > 0:
            raise Exception("Missing required fields {}".format(', '.join(missing_fields)))
        super(BaseResource, self).__init__(**kwargs)

    @property
    def required_fields(self):
        value = BaseObject.required_fields.fget()
        return value

    @required_fields.setter
    def required_fields(self, value):
        BaseObject.required_fields.fset(self, value)

    @property
    def optional_fields(self):
        value = BaseObject.optional_fields.fget()
        return value

    @optional_fields.setter
    def optional_fields(self, value):
        BaseObject.optional_fields.fset(self, value)


class Account(BaseResource):
    required_fields = ["id", "number", "name", "balance", "type", "status",
                       "customerId", "institutionId", "createdDate", ]
    optional_fields = ["aggregationStatusCode", "aggregationSuccessDate",
                       "aggregationAttemptDate", "balanceDate", "lastUpdatedDate",
                       "detail", ]

    _account_types = ['unknown', 'checking', 'savings', 'cd', 'moneyMarket',
                      'creditCard', 'lineOfCredit', 'investment', 'mortgage', 'loan']
    AccountTypes = enum(**{a.upper(): a for a in _account_types})

    @classmethod
    def deserialize(cls, account):
        if 'detail' in account:
            AT = cls.AccountTypes
            account_type = account.get('type')
            if account_type == AT.INVESTMENT:
                account_class = InvestmentAccount
            elif account_type in [AT.CREDIT_CARD, AT.LINEOFCREDIT]:
                account_class = CreditCardAccount
            elif account_type in [AT.MORTGAGE, AT.LOAD]:
                account_class = LoanAccount
            else:
                account_class = ChequingAccount
            account['detail'] = account_class(**account['detail'])
        # else:
        #     account['detail'] = None
        return Account(**account)


class ChequingAccount(BaseResource):
    required_fields = ["availableBalanceAmount", "interestYtdAmount",
                       "periodInterestRate", "periodInterestAmount", ]


class CreditCardAccount(BaseResource):
    required_fields = ["creditMaxAmount", "creditAvailableAmount", "paymentMinAmount",
                       "paymentDueDate", "lastPaymentAmount", "lastPaymentDate",
                       "interestRate", "cashAdvanceInterestRate", ]

class LoanAccount(BaseResource):
    required_fields = ["interestRate", "nextPaymentDate", "nextPayment", "escrowBalance",
                       "payoffAmount", "principalBalance", "ytdInterestPaid",
                       "ytdPrincipalPaid", "lastPaymentAmount", "lastPaymentReceiveDate", ]

class InvestmentAccount(BaseResource):
    required_fields = ["availableCashBalance", ]


class Institution(BaseResource):
    required_fields = ["id", "name", "accountTypeDescription", "urlHomeApp",
                       "urlLogonApp", "urlProductApp", ]


class LoginField(BaseResource):
    required_fields = ["id", "name", "value", "description", "displayOrder",
                       "mask", "instructions", ]
    optional_fields = ["valueLengthMin", "valueLengthMax", ]


class Customer(BaseResource):
    required_fields = ["username", "firstName", "lastName",]
    optional_fields = ["id", "type", "createdDate", ]



class MFAChallenge(BaseResource):
    required_fields = ["session", "questions", ]


class BaseMFA(BaseResource):
    required_fields = ["text", "answer", ]

    @classmethod
    def deserialize(cls, question):
        if 'image' in question:
            return CaptchaMFA(text=question.get("text"),
                                   image=question.get("image"),
                                   answer="")
        elif 'choice' in question:
            choices = [c["@value"] for c in question.get("choice")]
            return MultipleOptionsMFA(text=question.get("text"),
                                           choices=choices,
                                           answer="")
        elif 'imageChoice' in question:
            choices = [(c["@value"], c["#text"]) for c in question.get("imageChoice")]
            return MultipleImagesMFA(text=question.get("text"),
                                          imageChoices=choices,
                                          answer="")
        else:
            return TextMFA(text=question.get("text"), answer="")


class TextMFA(BaseMFA):
    pass

class CaptchaMFA(BaseMFA):
    required_fields = ["image", ]


class MultipleOptionsMFA(BaseMFA):
    required_fields = ["choices", ]


class MultipleImagesMFA(BaseMFA):
    required_fields = ["imageChoices", ]


