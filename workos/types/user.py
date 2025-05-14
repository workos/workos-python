from typing import Optional
from workos.types.password_hash_type import PasswordHashType

class UpdateUserOptions:
    def __init__(
        self,
        user_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
        external_id: Optional[str] = None,
    ):
        self.user_id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.email_verified = email_verified
        self.password = password
        self.password_hash = password_hash
        self.password_hash_type = password_hash_type
        self.external_id = external_id


class SerializedUpdateUserOptions:
    def __init__(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
        external_id: Optional[str] = None,
    ):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.email_verified = email_verified
        self.password = password
        self.password_hash = password_hash
        self.password_hash_type = password_hash_type
        self.external_id = external_id