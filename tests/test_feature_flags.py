from typing import Union
import pytest
from tests.utils.fixtures.mock_feature_flag import MockFeatureFlag
from tests.utils.syncify import syncify
from workos.feature_flags import AsyncFeatureFlags, FeatureFlags


@pytest.mark.sync_and_async(FeatureFlags, AsyncFeatureFlags)
class TestFeatureFlags:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[FeatureFlags, AsyncFeatureFlags]):
        self.http_client = module_instance._http_client
        self.feature_flags = module_instance

    @pytest.fixture
    def mock_feature_flag(self):
        return MockFeatureFlag("flag_01").dict()

    @pytest.fixture
    def mock_feature_flag_enabled(self):
        return MockFeatureFlag("flag_01", enabled=True).dict()

    @pytest.fixture
    def mock_feature_flag_disabled(self):
        return MockFeatureFlag("flag_01", enabled=False).dict()

    @pytest.fixture
    def mock_feature_flags_list(self):
        return {
            "data": [MockFeatureFlag(id=f"flag_{i}").dict() for i in range(3)],
            "object": "list",
            "list_metadata": {"before": None, "after": None},
        }

    def test_list_feature_flags(
        self, mock_feature_flags_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_feature_flags_list, 200
        )

        result = syncify(self.feature_flags.list_feature_flags())

        def to_dict(x):
            return x.dict()

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/feature-flags")
        assert list(map(to_dict, result.data)) == mock_feature_flags_list["data"]

    def test_get_feature_flag(
        self, mock_feature_flag, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_feature_flag, 200
        )

        result = syncify(self.feature_flags.get_feature_flag("test-feature"))

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/feature-flags/test-feature")
        assert result.slug == "test-feature"
        assert result.id == "flag_01"

    def test_enable_feature_flag(
        self, mock_feature_flag_enabled, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_feature_flag_enabled, 200
        )

        result = syncify(self.feature_flags.enable_feature_flag("test-feature"))

        assert request_kwargs["method"] == "put"
        assert request_kwargs["url"].endswith("/feature-flags/test-feature/enable")
        assert result.enabled is True

    def test_disable_feature_flag(
        self, mock_feature_flag_disabled, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_feature_flag_disabled, 200
        )

        result = syncify(self.feature_flags.disable_feature_flag("test-feature"))

        assert request_kwargs["method"] == "put"
        assert request_kwargs["url"].endswith("/feature-flags/test-feature/disable")
        assert result.enabled is False

    def test_add_feature_flag_target(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, None, 200
        )

        result = syncify(
            self.feature_flags.add_feature_flag_target("test-feature", "org_01ABC")
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/feature-flags/test-feature/targets/org_01ABC"
        )
        assert result is None

    def test_remove_feature_flag_target(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, None, 200
        )

        result = syncify(
            self.feature_flags.remove_feature_flag_target("test-feature", "user_01XYZ")
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/feature-flags/test-feature/targets/user_01XYZ"
        )
        assert result is None
