# @oagen-ignore-file
# This file is hand-maintained. PKCE (Proof Key for Code Exchange) utilities
# for OAuth 2.0 public client flows. These are client-side cryptographic
# helpers that will always be hand-maintained.

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class PKCEPair:
    """A PKCE code verifier and challenge pair."""

    code_verifier: str
    code_challenge: str
    code_challenge_method: Literal["S256"]


def _base64url_encode(data: bytes) -> str:
    """Base64url-encode bytes without padding, per RFC 7636."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class PKCE:
    """PKCE (RFC 7636) code verifier and challenge utilities.

    All operations are synchronous and stateless -- no client or async
    variant is needed.
    """

    def generate_code_verifier(self, length: int = 43) -> str:
        """Generate a cryptographically random code verifier.

        Args:
            length: Length of the verifier string (43-128 per RFC 7636).

        Returns:
            A base64url-encoded random string of the requested length.

        Raises:
            ValueError: If length is outside the 43-128 range.
        """
        if length < 43 or length > 128:
            raise ValueError(
                f"Code verifier length must be between 43 and 128, got {length}"
            )
        num_bytes = (length * 3 + 3) // 4
        raw = os.urandom(num_bytes)
        return _base64url_encode(raw)[:length]

    def generate_code_challenge(self, verifier: str) -> str:
        """Compute the S256 code challenge for a given verifier.

        Args:
            verifier: The code verifier string.

        Returns:
            The base64url-encoded SHA-256 hash of the verifier.
        """
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return _base64url_encode(digest)

    def generate(self) -> PKCEPair:
        """Generate a complete PKCE pair (verifier + challenge).

        Returns:
            A PKCEPair with code_verifier, code_challenge, and
            code_challenge_method set to "S256".
        """
        verifier = self.generate_code_verifier()
        challenge = self.generate_code_challenge(verifier)
        return PKCEPair(
            code_verifier=verifier,
            code_challenge=challenge,
            code_challenge_method="S256",
        )
