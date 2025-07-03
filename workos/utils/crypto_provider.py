import os
from typing import Optional, Dict
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class CryptoProvider:
    def encrypt(
        self, plaintext: bytes, key: bytes, iv: bytes, aad: Optional[bytes]
    ) -> Dict[str, bytes]:
        encryptor = Cipher(
            algorithms.AES(key), modes.GCM(iv), backend=default_backend()
        ).encryptor()

        if aad:
            encryptor.authenticate_additional_data(aad)

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return {"ciphertext": ciphertext, "iv": iv, "tag": encryptor.tag}

    def decrypt(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
        tag: bytes,
        aad: Optional[bytes] = None,
    ) -> bytes:
        decryptor = Cipher(
            algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
        ).decryptor()

        if aad:
            decryptor.authenticate_additional_data(aad)

        return decryptor.update(ciphertext) + decryptor.finalize()

    def random_bytes(self, n: int) -> bytes:
        return os.urandom(n)
