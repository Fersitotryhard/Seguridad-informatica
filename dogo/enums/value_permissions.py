from enum import Enum

class ValuePermissions(Enum):
    CUSTOMER_EDIT = 1
    CUSTOMER_DELETE = 2
    ACCOUNT = 3
    TRANSACTIONS_COMMIT = 4