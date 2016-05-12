

class BaseObject(object):
    required_fields = []
    optional_fields = []

    def __init__(self, **kwargs):
        missing_fields = []
        for field in self.get_required_fields():
            if field not in kwargs:
                missing_fields.append(field)

        if len(missing_fields) > 0:
            raise Exception("Missing required fields {}".format(', '.join(missing_fields)))

        for key, value in kwargs.items():
            if key in self.get_optional_fields():
                self.__dict__.update({key: value})

    def get_required_fields(self):
        return self.required_fields

    def get_optional_fields(self):
        return self.optional_fields


class BaseResource(BaseObject):
    def get_required_fields(self):
        fields = super(BaseResource, self).get_required_fields()
        return fields.extend(self.required_fields)

    def get_optional_fields(self):
        fields = super(BaseResource, self).get_required_fields()
        return fields.extend(self.optional_fields)


class Account(BaseResource):
    required_fields = ["id", "number", "name", "balance", "type", "status",
                       "customerId", "institutionId", "createdDate", ]
    optional_fields = ["aggregationStatusCode", "aggregationSuccessDate",
                       "aggregationAttemptDate", "balanceDate", "lastUpdatedDate",
                       "detail", ]

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
                       "mask", "valueLengthMin", "valueLengthMax", "instructions", ]


class Customer(BaseResource):
    required_fields = ["username", "firstName", "lastName",]
    optional_fields = ["id", "type", "createdDate", ]



class MFAChallenge(BaseResource):
    required_fields = ["session", "questions", ]


class BaseMFA(BaseResource):
    required_fields = ["text", "answer", ]


class TextMFA(BaseMFA):
    pass


class CaptchaMFA(BaseMFA):
    required_fields = ["image", ]


class MultipleOptionsMFA(BaseMFA):
    required_fields = ["choices", ]


class MultipleImagesMFA(BaseMFA):
    required_fields = ["imageChoices", ]


