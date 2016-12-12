from .utils import enum


class BaseObject(object):
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
        # TODO: Find a better way to handle when required fields are not specified
        try:
            return BaseObject.required_fields.fget()
        except TypeError:
            return []

    @required_fields.setter
    def required_fields(self, value):
        BaseObject.required_fields.fset(self, value)

    @property
    def optional_fields(self):
        #TODO: Find a better way to handle when optional fields are not specified
        try:
            return BaseObject.optional_fields.fget()
        except TypeError:
            return []

    @optional_fields.setter
    def optional_fields(self, value):
        BaseObject.optional_fields.fset(self, value)

    def __repr__(self):
        if isinstance(self, Customer):
            return "<{}>".format(self.__class__.__name__)
        else:
            return "<{}: {}>".format(self.__class__.__name__, self.id)


class Account(BaseResource):
    required_fields = ["id", "number", "name", "balance", "type", "status",]
    optional_fields = ["customerId", "institutionId", "createdDate",
                       "aggregationStatusCode", "aggregationSuccessDate",
                       "aggregationAttemptDate", "balanceDate", "lastUpdatedDate",
                       "detail", 'institutionLoginId']

    _account_types = ['unknown', 'checking', 'savings', 'cd', 'moneyMarket',
                      'creditCard', 'lineOfCredit', 'investment', 'mortgage', 'loan']
    AccountTypes = enum(**{a.upper(): a for a in _account_types})

    @classmethod
    def deserialize(cls, account):
        if account.get('detail', None) is not None:
            AT = cls.AccountTypes
            account_type = account.get('type')
            if account_type == AT.INVESTMENT:
                account_class = InvestmentAccount
            elif account_type in [AT.CREDITCARD, AT.LINEOFCREDIT]:
                account_class = CreditCardAccount
            elif account_type in [AT.MORTGAGE, AT.LOAN]:
                account_class = LoanAccount
            else:
                account_class = CheckingAccount
            account['detail'] = account_class(**account['detail'])
        return Account(**account)

    def to_json(self):
        return {
            'id' : self.id,
            'number' : self.number,
            'name' : self.name,
            'balance' : self.balance,
            'type' : self.type,
            'status' : self.status,
        }

    def to_jsonl(self):
        return {
            'id' : self.id,
            'number' : self.number,
            'name' : self.name,
            'type' : self.type,
            'status' : self.status
        }



class CheckingAccount(BaseResource):
    optional_fields = ["availableBalanceAmount", "interestYtdAmount",
                       "periodInterestRate", "periodInterestAmount", ]

    def to_json(self):
        return {
            'id' : self.id,
            'number' : self.number,
            'name' : self.name,
            'balance' : self.balance,
            'type' : self.type,
            'status' : self.status,
        }


class CreditCardAccount(BaseResource):
    optional_fields = ["creditMaxAmount", "creditAvailableAmount", "paymentMinAmount",
                       "paymentDueDate", "lastPaymentAmount", "lastPaymentDate",
                       "interestRate", "cashAdvanceInterestRate", ]

    def to_json(self):
        return {
            'id' : self.id,
            'number' : self.number,
            'name' : self.name,
            'balance' : self.balance,
            'type' : self.type,
            'status' : self.status,
        }



class LoanAccount(BaseResource):
    optional_fields = ["interestRate", "nextPaymentDate", "nextPayment", "escrowBalance",
                       "payoffAmount", "principalBalance", "ytdInterestPaid",
                       "ytdPrincipalPaid", "lastPaymentAmount", "lastPaymentReceiveDate", ]


    def to_json(self):
        return {
            'id' : self.id,
            'number' : self.number,
            'name' : self.name,
            'balance' : self.balance,
            'type' : self.type,
            'status' : self.status,
        }


class InvestmentAccount(BaseResource):
    optional_fields = ["availableCashBalance", ]


    def to_json(self):
        return {
            'id' : self.id,
            'number' : self.number,
            'name' : self.name,
            'balance' : self.balance,
            'type' : self.type,
            'status' : self.status,
        }


class Institution(BaseResource):
    required_fields = ["id", "name", "accountTypeDescription", "urlHomeApp",
                       "urlLogonApp", "urlProductApp", ]

    def to_json(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'accountTypeDescription' : self.accountTypeDescription,
            'urlHomeApp' : self.urlHomeApp,
            'urlLogonApp' : self.urlLogonApp,
            'urlProductApp' : self.urlProductApp
        }


class LoginField(BaseResource):
    required_fields = ["id", "name", "value", "description", "displayOrder",
                       "mask", "instructions", ]
    optional_fields = ["valueLengthMin", "valueLengthMax", ]

    def to_json(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'value' : self.value,
            'description' : self.description,
            'displayOrder' : self.displayOrder,
            'mask' : self.mask,
            'instructions' : self.instructions
        }


class Customer(BaseResource):
    required_fields = ["username", "firstName", "lastName", ]
    optional_fields = ["id", "type", "createdDate", ]

    def to_json(self):
        return {
            'username' : self.username,
            'firstName' : self.firstName,
            'lastName' : self.lastName,
            'id' : self.id
        }


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


class Transaction(BaseResource):
    _txn_types = ['atm', 'cash', 'check', 'credit', 'debit', 'deposit',
                  'directDebit', 'directDeposit', 'dividend', 'fee',
                  'interest', 'other', 'payment', 'pointOfSale', 'repeatPayment',
                  'serviceCharge', 'transfer']

    TransactionTypes = enum(**{t.upper(): t for t in _txn_types})

    _txn_statuses = ['active', 'pending', 'shadow']

    TransactionStatuses = enum(**{s.upper(): s for s in _txn_statuses})

    required_fields = ["id", "accountId", "amount", "createdDate", "customerId",
                       "description", "institutionTransactionId", "postedDate",
                       "status", "transactionDate"]

    optional_fields = ["bonusAmount", "checkNum", "escrowAmount", "feeAmount",
                       "interestAmount", "memo", "principalAmount", "subaccount", "type",
                       "unitQuantity", "unitValue"]