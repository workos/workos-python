from typing import Literal

SmsAuthenticationFactorType = Literal["sms"]
TotpAuthenticationFactorType = Literal["totp"]

EnrollAuthenticationFactorType = Literal[
    SmsAuthenticationFactorType, TotpAuthenticationFactorType
]
