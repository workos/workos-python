from workos._types import NOT_GIVEN, NotGiven


class TestNotGiven:
    """The NOT_GIVEN sentinel is the default for nullable optional params,
    letting generated methods tell an omitted argument apart from an explicit
    None (which clears the field via JSON null)."""

    def test_is_falsy(self):
        assert not NOT_GIVEN
        assert bool(NOT_GIVEN) is False

    def test_repr(self):
        assert repr(NOT_GIVEN) == "NOT_GIVEN"

    def test_is_distinct_from_none(self):
        assert NOT_GIVEN is not None
        assert isinstance(NOT_GIVEN, NotGiven)

    def test_exported_from_public_namespace(self):
        import workos

        assert workos.NOT_GIVEN is NOT_GIVEN
        assert workos.NotGiven is NotGiven
