from workos.utils.pagination_order import Order
from workos.utils.auto_pagination import auto_paginate, timestamp_compare


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

    def auto_paging_iter(self):
        data = self.to_dict()["data"]
        list_metadata = self.to_dict()["list_metadata"]
        list_type = data[0]["object"]
        after = list_metadata["after"]
        before = list_metadata["before"]

        if data[0].get("directory_id"):
            parent_resource_id = data[0]["directory_id"]
        else:
            parent_resource_id = None

        result = auto_paginate(list_type, data, after, before, parent_resource_id)
        return result
