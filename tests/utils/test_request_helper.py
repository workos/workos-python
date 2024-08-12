from workos.utils.request_helper import RequestHelper


class TestRequestHelper:

    def test_build_parameterized_url(self):
        assert RequestHelper.build_parameterized_path(path="a/b/c") == "a/b/c"
        assert RequestHelper.build_parameterized_path(path="a/{b}/c", b="b") == "a/b/c"
        assert (
            RequestHelper.build_parameterized_path(path="a/{b}/c", b="test")
            == "a/test/c"
        )
        assert (
            RequestHelper.build_parameterized_path(
                path="a/{b}/c", b="i/am/being/sneaky"
            )
            == "a/i/am/being/sneaky/c"
        )
