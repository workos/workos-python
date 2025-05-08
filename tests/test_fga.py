import pytest

from workos.exceptions import (
    AuthenticationException,
    BadRequestException,
    NotFoundException,
    ServerException,
)
from workos.fga import FGA
from workos.types.fga import (
    WarrantCheckInput,
    WarrantWrite,
    SubjectInput,
)


class TestValidation:
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.fga = FGA(http_client=self.http_client)

    def test_get_resource_no_resources(self):
        with pytest.raises(ValueError):
            self.fga.get_resource(resource_type="", resource_id="test")

        with pytest.raises(ValueError):
            self.fga.get_resource(resource_type="test", resource_id="")

    def test_create_resource_no_resources(self):
        with pytest.raises(ValueError):
            self.fga.create_resource(resource_type="", resource_id="test", meta={})

        with pytest.raises(ValueError):
            self.fga.create_resource(resource_type="test", resource_id="", meta={})

    def test_update_resource_no_resources(self):
        with pytest.raises(ValueError):
            self.fga.update_resource(resource_type="", resource_id="test", meta={})

        with pytest.raises(ValueError):
            self.fga.update_resource(resource_type="test", resource_id="", meta={})

    def test_delete_resource_no_resources(self):
        with pytest.raises(ValueError):
            self.fga.delete_resource(resource_type="", resource_id="test")

        with pytest.raises(ValueError):
            self.fga.delete_resource(resource_type="test", resource_id="")

    def test_batch_write_warrants_no_batch(self):
        with pytest.raises(ValueError):
            self.fga.batch_write_warrants(batch=[])

    def test_check_no_checks(self):
        with pytest.raises(ValueError):
            self.fga.check(op="any_of", checks=[])


class TestErrorHandling:
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.fga = FGA(http_client=self.http_client)

    @pytest.fixture
    def mock_404_response(self):
        return {
            "code": "not_found",
            "message": "test message",
            "type": "some-type",
            "key": "nonexistent-type",
        }

    @pytest.fixture
    def mock_400_response(self):
        return {"code": "invalid_request", "message": "test message"}

    def test_get_resource_404(self, mock_404_response, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_404_response, 404)

        with pytest.raises(NotFoundException):
            self.fga.get_resource(resource_type="test", resource_id="test")

    def test_get_resource_400(self, mock_400_response, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_400_response, 400)

        with pytest.raises(BadRequestException):
            self.fga.get_resource(resource_type="test", resource_id="test")

    def test_get_resource_500(self, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, status_code=500)

        with pytest.raises(ServerException):
            self.fga.get_resource(resource_type="test", resource_id="test")

    def test_get_resource_401(self, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, status_code=401)

        with pytest.raises(AuthenticationException):
            self.fga.get_resource(resource_type="test", resource_id="test")


class TestWarnings:
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.fga = FGA(http_client=self.http_client)

    def test_check_with_warning(self, mock_http_client_with_response):
        mock_response = {
            "result": "authorized",
            "is_implicit": True,
            "warnings": [
                {
                    "code": "missing_context_keys",
                    "message": "Missing context keys",
                    "keys": ["key1", "key2"],
                }
            ],
        }
        mock_http_client_with_response(self.http_client, mock_response, 200)

        response = self.fga.check(
            op="any_of",
            checks=[
                WarrantCheckInput(
                    resource_type="schedule",
                    resource_id="schedule-A1",
                    relation="viewer",
                    subject=SubjectInput(resource_type="user", resource_id="user-A"),
                )
            ],
        )
        assert response.dict(exclude_none=True) == mock_response

    def test_query_with_warning(self, mock_http_client_with_response):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "resource_type": "user",
                    "resource_id": "richard",
                    "relation": "member",
                    "warrant": {
                        "resource_type": "role",
                        "resource_id": "developer",
                        "relation": "member",
                        "subject": {"resource_type": "user", "resource_id": "richard"},
                    },
                    "is_implicit": True,
                }
            ],
            "list_metadata": {},
            "warnings": [
                {
                    "code": "missing_context_keys",
                    "message": "Missing context keys",
                    "keys": ["key1", "key2"],
                }
            ],
        }

        mock_http_client_with_response(self.http_client, mock_response, 200)

        response = self.fga.query(
            q="select member of type user for permission:view-docs",
            order="asc",
            warrant_token="warrant_token",
        )
        assert response.dict(exclude_none=True) == mock_response

    def test_check_with_generic_warning(self, mock_http_client_with_response):
        mock_response = {
            "result": "authorized",
            "is_implicit": True,
            "warnings": [
                {
                    "code": "generic",
                    "message": "Generic warning",
                }
            ],
        }

        mock_http_client_with_response(self.http_client, mock_response, 200)

        response = self.fga.check(
            op="any_of",
            checks=[
                WarrantCheckInput(
                    resource_type="schedule",
                    resource_id="schedule-A1",
                    relation="viewer",
                    subject=SubjectInput(resource_type="user", resource_id="user-A"),
                )
            ],
        )
        assert response.dict(exclude_none=True) == mock_response


class TestFGA:
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.fga = FGA(http_client=self.http_client)

    @pytest.fixture
    def mock_get_resource_response(self):
        return {
            "resource_type": "test",
            "resource_id": "first-resource",
            "meta": {"my_key": "my_val"},
            "created_at": "2022-02-15T15:14:19.392Z",
        }

    def test_get_resource(
        self, mock_get_resource_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_get_resource_response, 200
        )
        enroll_factor = self.fga.get_resource(
            resource_type=mock_get_resource_response["resource_type"],
            resource_id=mock_get_resource_response["resource_id"],
        )
        assert enroll_factor.dict(exclude_none=True) == mock_get_resource_response

    @pytest.fixture
    def mock_list_resources_response(self):
        return {
            "object": "list",
            "data": [
                {
                    "resource_type": "test",
                    "resource_id": "third-resource",
                    "meta": {"my_key": "my_val"},
                },
                {
                    "resource_type": "test",
                    "resource_id": "{{ createResourceWithGeneratedId.resource_id }}",
                },
                {"resource_type": "test", "resource_id": "second-resource"},
                {"resource_type": "test", "resource_id": "first-resource"},
            ],
            "list_metadata": {},
        }

    def test_list_resources(
        self, mock_list_resources_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_list_resources_response, 200
        )
        response = self.fga.list_resources()
        assert response.dict(exclude_none=True) == mock_list_resources_response

    @pytest.fixture
    def mock_create_resource_response(self):
        return {
            "resource_type": "test",
            "resource_id": "third-resource",
            "meta": {"my_key": "my_val"},
        }

    def test_create_resource(
        self, mock_create_resource_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_create_resource_response, 200
        )
        response = self.fga.create_resource(
            resource_type=mock_create_resource_response["resource_type"],
            resource_id=mock_create_resource_response["resource_id"],
            meta=mock_create_resource_response["meta"],
        )
        assert response.dict(exclude_none=True) == mock_create_resource_response

    @pytest.fixture
    def mock_update_resource_response(self):
        return {
            "resource_type": "test",
            "resource_id": "third-resource",
            "meta": {"my_updated_key": "my_updated_value"},
        }

    def test_update_resource(
        self, mock_update_resource_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_update_resource_response, 200
        )
        response = self.fga.update_resource(
            resource_type=mock_update_resource_response["resource_type"],
            resource_id=mock_update_resource_response["resource_id"],
            meta=mock_update_resource_response["meta"],
        )
        assert response.dict(exclude_none=True) == mock_update_resource_response

    def test_delete_resource(self, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, status_code=200)
        self.fga.delete_resource(resource_type="test", resource_id="third-resource")

    @pytest.fixture
    def mock_list_resource_types_response(self):
        return {
            "object": "list",
            "data": [
                {
                    "type": "feature",
                    "relations": {
                        "member": {
                            "inherit_if": "any_of",
                            "rules": [
                                {
                                    "inherit_if": "member",
                                    "of_type": "feature",
                                    "with_relation": "member",
                                },
                                {
                                    "inherit_if": "member",
                                    "of_type": "pricing-tier",
                                    "with_relation": "member",
                                },
                                {
                                    "inherit_if": "member",
                                    "of_type": "tenant",
                                    "with_relation": "member",
                                },
                            ],
                        }
                    },
                },
                {
                    "type": "permission",
                    "relations": {
                        "member": {
                            "inherit_if": "any_of",
                            "rules": [
                                {
                                    "inherit_if": "member",
                                    "of_type": "permission",
                                    "with_relation": "member",
                                },
                                {
                                    "inherit_if": "member",
                                    "of_type": "role",
                                    "with_relation": "member",
                                },
                            ],
                        }
                    },
                },
                {
                    "type": "pricing-tier",
                    "relations": {
                        "member": {
                            "inherit_if": "any_of",
                            "rules": [
                                {
                                    "inherit_if": "member",
                                    "of_type": "pricing-tier",
                                    "with_relation": "member",
                                },
                                {
                                    "inherit_if": "member",
                                    "of_type": "tenant",
                                    "with_relation": "member",
                                },
                            ],
                        }
                    },
                },
            ],
            "list_metadata": {"after": "after_token"},
        }

    def test_list_resource_types(
        self, mock_list_resource_types_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_list_resource_types_response, 200
        )
        response = self.fga.list_resource_types()
        assert response.dict(exclude_none=True) == mock_list_resource_types_response

    @pytest.fixture
    def mock_list_warrants_response(self):
        return {
            "object": "list",
            "data": [
                {
                    "resource_type": "permission",
                    "resource_id": "view-balance-sheet",
                    "relation": "member",
                    "subject": {
                        "resource_type": "role",
                        "resource_id": "senior-accountant",
                        "relation": "member",
                    },
                },
                {
                    "resource_type": "permission",
                    "resource_id": "balance-sheet:edit",
                    "relation": "member",
                    "subject": {"resource_type": "user", "resource_id": "user-b"},
                },
            ],
            "list_metadata": {},
        }

    def test_list_warrants(
        self, mock_list_warrants_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_list_warrants_response, 200
        )
        response = self.fga.list_warrants()
        assert response.dict(exclude_none=True) == mock_list_warrants_response

    @pytest.fixture
    def mock_write_warrant_response(self):
        return {"warrant_token": "warrant_token"}

    def test_write_warrant(
        self, mock_write_warrant_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_write_warrant_response, 200
        )

        response = self.fga.write_warrant(
            op="create",
            subject_type="role",
            subject_id="senior-accountant",
            subject_relation="member",
            relation="member",
            resource_type="permission",
            resource_id="view-balance-sheet",
        )
        assert response.dict(exclude_none=True) == mock_write_warrant_response

    def test_batch_write_warrants(
        self, mock_write_warrant_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_write_warrant_response, 200
        )

        response = self.fga.batch_write_warrants(
            batch=[
                WarrantWrite(
                    op="create",
                    resource_type="permission",
                    resource_id="view-balance-sheet",
                    relation="member",
                    subject=SubjectInput(
                        resource_type="role",
                        resource_id="senior-accountant",
                        relation="member",
                    ),
                ),
                WarrantWrite(
                    op="create",
                    resource_type="permission",
                    resource_id="balance-sheet:edit",
                    relation="member",
                    subject=SubjectInput(
                        resource_type="user",
                        resource_id="user-b",
                    ),
                ),
            ]
        )
        assert response.dict(exclude_none=True) == mock_write_warrant_response

    @pytest.fixture
    def mock_check_warrant_response(self):
        return {"result": "authorized", "is_implicit": True}

    def test_check(self, mock_check_warrant_response, mock_http_client_with_response):
        mock_http_client_with_response(
            self.http_client, mock_check_warrant_response, 200
        )

        response = self.fga.check(
            op="any_of",
            checks=[
                WarrantCheckInput(
                    resource_type="schedule",
                    resource_id="schedule-A1",
                    relation="viewer",
                    subject=SubjectInput(resource_type="user", resource_id="user-A"),
                )
            ],
        )
        assert response.dict(exclude_none=True) == mock_check_warrant_response

    @pytest.fixture
    def mock_check_response_with_debug_info(self):
        return {
            "result": "authorized",
            "is_implicit": False,
            "debug_info": {
                "processing_time": 123,
                "decision_tree": {
                    "check": {
                        "resource_type": "report",
                        "resource_id": "report-a",
                        "relation": "editor",
                        "subject": {"resource_type": "user", "resource_id": "user-b"},
                        "context": {"tenant": "tenant-b"},
                    },
                    "policy": 'tenant == "tenant-b"',
                    "decision": "eval_policy",
                    "processing_time": 123,
                    "children": [
                        {
                            "check": {
                                "resource_type": "role",
                                "resource_id": "admin",
                                "relation": "member",
                                "subject": {
                                    "resource_type": "user",
                                    "resource_id": "user-b",
                                },
                                "context": {"tenant": "tenant-b"},
                            },
                            "policy": 'tenant == "tenant-b"',
                            "decision": "eval_policy",
                            "processing_time": 123,
                        }
                    ],
                },
            },
        }

    def test_check_with_debug_info(
        self, mock_check_response_with_debug_info, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            self.http_client, mock_check_response_with_debug_info, 200
        )

        response = self.fga.check(
            op="any_of",
            checks=[
                WarrantCheckInput(
                    resource_type="report",
                    resource_id="report-a",
                    relation="editor",
                    subject=SubjectInput(resource_type="user", resource_id="user-b"),
                    context={"tenant": "tenant-b"},
                )
            ],
            debug=True,
        )
        assert response.dict(exclude_none=True) == mock_check_response_with_debug_info

    @pytest.fixture
    def mock_batch_check_response(self):
        return [
            {"result": "authorized", "is_implicit": True},
            {"result": "not_authorized", "is_implicit": True},
        ]

    def test_check_batch(
        self, mock_batch_check_response, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_batch_check_response, 200)

        response = self.fga.check_batch(
            checks=[
                WarrantCheckInput(
                    resource_type="schedule",
                    resource_id="schedule-A1",
                    relation="viewer",
                    subject=SubjectInput(resource_type="user", resource_id="user-A"),
                ),
                WarrantCheckInput(
                    resource_type="schedule",
                    resource_id="schedule-A1",
                    relation="editor",
                    subject=SubjectInput(resource_type="user", resource_id="user-B"),
                ),
            ]
        )

        assert [
            r.dict(exclude_none=True) for r in response
        ] == mock_batch_check_response

    @pytest.fixture
    def mock_query_response(self):
        return {
            "object": "list",
            "data": [
                {
                    "resource_type": "user",
                    "resource_id": "richard",
                    "relation": "member",
                    "warrant": {
                        "resource_type": "role",
                        "resource_id": "developer",
                        "relation": "member",
                        "subject": {"resource_type": "user", "resource_id": "richard"},
                    },
                    "is_implicit": True,
                },
                {
                    "resource_type": "user",
                    "resource_id": "tom",
                    "relation": "member",
                    "warrant": {
                        "resource_type": "role",
                        "resource_id": "manager",
                        "relation": "member",
                        "subject": {"resource_type": "user", "resource_id": "tom"},
                    },
                    "is_implicit": True,
                },
            ],
            "list_metadata": {},
        }

    def test_query(self, mock_query_response, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_query_response, 200)

        response = self.fga.query(
            q="select member of type user for permission:view-docs",
            order="asc",
            warrant_token="warrant_token",
        )
        assert response.dict(exclude_none=True) == mock_query_response

    def test_query_with_context(
        self, mock_query_response, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_query_response, 200
        )

        response = self.fga.query(
            q="select member of type user for permission:view-docs",
            order="asc",
            warrant_token="warrant_token",
            context={"region": "us", "subscription": "pro"},
        )

        assert request_kwargs["url"] == "https://api.workos.test/fga/v1/query"
        expected_full_url = "https://api.workos.test/fga/v1/query?q=select+member+of+type+user+for+permission%3Aview-docs&limit=10&order=asc&context=%7B%22region%22%3A+%22us%22%2C+%22subscription%22%3A+%22pro%22%7D"
        assert request_kwargs["full_url"] == expected_full_url
        assert response.dict(exclude_none=True) == mock_query_response
