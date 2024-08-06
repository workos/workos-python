from math import e
import pytest
from pydantic import TypeAdapter, ValidationError
from workos.types.directory_sync.directory_state import DirectoryState


class TestDirectoryState:
    @pytest.fixture
    def directory_state_type_adapter(self):
        return TypeAdapter(DirectoryState)

    def test_convert_linked_to_active(self, directory_state_type_adapter):
        assert directory_state_type_adapter.validate_python("active") == "active"
        assert directory_state_type_adapter.validate_python("linked") == "active"
        try:
            directory_state_type_adapter.validate_python("foo")
        except ValidationError as e:
            assert e.errors()[0]["type"] == "literal_error"

    def test_convert_unlinked_to_inactive(self, directory_state_type_adapter):
        assert directory_state_type_adapter.validate_python("unlinked") == "inactive"
        assert directory_state_type_adapter.validate_python("inactive") == "inactive"

    def test_invalid_values_returns_validation_error(
        self, directory_state_type_adapter
    ):
        try:
            directory_state_type_adapter.validate_python("foo")
        except ValidationError as e:
            assert e.errors()[0]["type"] == "literal_error"

        try:
            directory_state_type_adapter.validate_python(None)
        except ValidationError as e:
            assert e.errors()[0]["type"] == "literal_error"

        try:
            directory_state_type_adapter.validate_python(5)
        except ValidationError as e:
            assert e.errors()[0]["type"] == "literal_error"

        try:
            directory_state_type_adapter.validate_python({"definitely": "not a state"})
        except ValidationError as e:
            assert e.errors()[0]["type"] == "literal_error"
