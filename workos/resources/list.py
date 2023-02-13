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
        after = self.to_dict()["list_metadata"]["after"]
        list_type = self.to_dict()["data"][0]["object"]
        all_items = self.to_dict()["data"]
        if len(all_items) > 1:
            order = timestamp_compare(
                all_items[0]["created_at"], all_items[1]["created_at"]
            )
        else:
            order = Order.Desc

        if list_type == "directory":
            result = auto_paginate(list_type, all_items, after, order)
            return result

        elif list_type == "directory_user":
            directory = self.to_dict()["data"][0]["directory_id"]
            result = auto_paginate(list_type, all_items, after, order, directory)
            return result

        elif list_type == "directory_group":
            directory = self.to_dict()["data"][0]["directory_id"]
            result = auto_paginate(list_type, all_items, after, order, directory)
            return result

        elif list_type == "organization":
            result = auto_paginate(list_type, all_items, after, order)
            return result

        elif list_type == "connection":
            result = auto_paginate(list_type, all_items, after, order)
            return result

        else:
            raise ValueError("Invalid list type")
