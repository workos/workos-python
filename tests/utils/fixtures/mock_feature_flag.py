import datetime

from workos.types.feature_flags.feature_flag import FeatureFlag


class MockFeatureFlag(FeatureFlag):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="feature_flag",
            id=id,
            slug="test-feature",
            name="Test Feature",
            description="A test feature flag",
            created_at=now,
            updated_at=now,
        )
