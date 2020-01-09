import pytest

import workos

@pytest.fixture
def set_api_key(monkeypatch):
    monkeypatch.setattr(workos, 'api_key', 'sk_abdsomecharactersm284')

@pytest.fixture
def set_project_id(monkeypatch):
    monkeypatch.setattr(workos, 'project_id', 'project_b27needthisforssotemxo')

@pytest.fixture
def set_api_key_and_project_id(set_api_key, set_project_id):
    pass