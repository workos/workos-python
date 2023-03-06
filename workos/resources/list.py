from workos.utils.pagination_order import Order
from workos.utils.list_types import Type, ParentResourceType
from workos.utils.auto_pagination import (
    get_response,
    timestamp_compare,
)


class WorkOSListResource(object):
    """Representation of a WorkOS List Resource as returned through the API.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSListResource is comprised of.
    """

    OBJECT_FIELDS = [
        "data",
        "list_metadata",
    ]

    @classmethod
    def construct_from_response(cls, response):
        """Returns an instance of WorkOSListResource.

        Args:
            response (dict): Resource data from a WorkOS API response

        Returns:
            WorkOSListResource: Instance of a WorkOSListResource with OBJECT_FIELDS fields set
        """
        obj = cls()
        for field in cls.OBJECT_FIELDS:
            setattr(obj, field, response.get(field))

        return obj

    def to_dict(self):
        """Returns a dict representation of the WorkOSListResource.

        Returns:
            dict: A dict representation of the WorkOSListResource
        """
        obj_dict = {}
        for field in self.OBJECT_FIELDS:
            obj_dict[field] = getattr(self, field, None)

        return obj_dict

    def auto_paginate(
        self,
        type=Type,
        parent_resource_id=None,
        parent_resource_type: ParentResourceType = None,
    ):

        data = self.to_dict()["data"]
        after = self.to_dict()["list_metadata"]["after"]
        before = self.to_dict()["list_metadata"]["before"]

        if before is None:
            if len(data) > 1:
                order = timestamp_compare(
                    data[0]["created_at"], data[len(data) - 1]["created_at"]
                )
                next_page_marker = after
                string_direction = "after"
            else:
                order = Order.Desc
                next_page_marker = after
                string_direction = "after"
        else:
            order = None
            next_page_marker = before
            string_direction = "before"

        params = {"type": type, "after": after, "before": before, "order": order}

        if parent_resource_id is not None and parent_resource_type is None:
            raise ValueError(
                "The parent_resource_type parameter must be included when parent_resource_id is included."
            )
        elif parent_resource_type is not None and parent_resource_id is None:
            raise ValueError(
                "The parent_resource_id parameter must be included when parent_resource_type is included."
            )

        if parent_resource_id is not None:
            params["parent_resource_id"] = parent_resource_id
            params["parent_resource_type"] = parent_resource_type.value
        while next_page_marker is not None:
            response = get_response(**params)
            for i in response["data"]:
                data.append(i)
            next_page_marker = response["list_metadata"][string_direction]
        return data
