from typing import Literal


PasswordHashType = Literal["bcrypt", "firebase-scrypt", "pbkdf2", "scrypt", "ssha"]
