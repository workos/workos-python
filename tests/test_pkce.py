import re

import pytest
from workos.pkce import PKCE, PKCEPair


class TestPKCE:
    def setup_method(self):
        self.pkce = PKCE()

    def test_generate_code_verifier_default_length(self):
        verifier = self.pkce.generate_code_verifier()
        assert len(verifier) == 43

    def test_generate_code_verifier_custom_length(self):
        verifier = self.pkce.generate_code_verifier(128)
        assert len(verifier) == 128

    def test_generate_code_verifier_min_length(self):
        verifier = self.pkce.generate_code_verifier(43)
        assert len(verifier) == 43

    def test_generate_code_verifier_rfc_characters(self):
        verifier = self.pkce.generate_code_verifier(128)
        assert re.match(r"^[A-Za-z0-9\-._~]+$", verifier)

    def test_generate_code_verifier_uniqueness(self):
        verifiers = {self.pkce.generate_code_verifier() for _ in range(100)}
        assert len(verifiers) == 100

    def test_generate_code_verifier_too_short(self):
        with pytest.raises(ValueError, match="43 and 128"):
            self.pkce.generate_code_verifier(42)

    def test_generate_code_verifier_too_long(self):
        with pytest.raises(ValueError, match="43 and 128"):
            self.pkce.generate_code_verifier(129)

    def test_generate_code_challenge_rfc_test_vector(self):
        verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        challenge = self.pkce.generate_code_challenge(verifier)
        assert challenge == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"

    def test_generate_code_challenge_deterministic(self):
        verifier = self.pkce.generate_code_verifier()
        c1 = self.pkce.generate_code_challenge(verifier)
        c2 = self.pkce.generate_code_challenge(verifier)
        assert c1 == c2

    def test_generate_code_challenge_no_padding(self):
        verifier = self.pkce.generate_code_verifier()
        challenge = self.pkce.generate_code_challenge(verifier)
        assert "=" not in challenge

    def test_generate_code_challenge_base64url_chars(self):
        verifier = self.pkce.generate_code_verifier()
        challenge = self.pkce.generate_code_challenge(verifier)
        assert re.match(r"^[A-Za-z0-9\-_]+$", challenge)

    def test_generate_returns_pkce_pair(self):
        pair = self.pkce.generate()
        assert isinstance(pair, PKCEPair)
        assert len(pair.code_verifier) == 43
        assert pair.code_challenge_method == "S256"

    def test_generate_challenge_matches_verifier(self):
        pair = self.pkce.generate()
        expected = self.pkce.generate_code_challenge(pair.code_verifier)
        assert pair.code_challenge == expected
