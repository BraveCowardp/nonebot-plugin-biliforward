from enum import Enum

class QrCodeStatus(Enum):
    SUCCESS = 0
    INVALID = 86038
    UNCONFIRMED = 86090
    UNSCANDE = 86101