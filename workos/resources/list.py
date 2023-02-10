import workos
from workos.utils.pagination_order import Order, timestamp_compare


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
            while after is not None:
                response = workos.client.directory_sync.list_directories(
                    limit=100, after=after, order=order
                )
                for i in response["data"]:
                    all_items.append(i)
                after = response["list_metadata"]["after"]
            return all_items

        elif list_type == "directory_user":
            directory = self.to_dict()["data"][0]["directory_id"]
            while after is not None:
                response = workos.client.directory_sync.list_users(
                    directory=directory,
                    limit=100,
                    after=after,
                    order=order,
                )
                for i in response["data"]:
                    all_items.append(i)
                after = response["list_metadata"]["after"]
            return all_items

        elif list_type == "directory_group":
            directory = self.to_dict()["data"][0]["directory_id"]
            while after is not None:
                response = workos.client.directory_sync.list_groups(
                    directory=directory,
                    limit=100,
                    after=after,
                    order=order,
                )
                for i in response["data"]:
                    all_items.append(i)
                after = response["list_metadata"]["after"]
            return all_items

        elif list_type == "organization":
            while after is not None:
                response = workos.client.organizations.list_organizations(
                    limit=100, after=after, order=order
                )
                for i in response["data"]:
                    all_items.append(i)
                after = response["list_metadata"]["after"]
            return all_items

        elif list_type == "connection":
            while after is not None:
                response = workos.client.sso.list_connections(
                    limit=100, after=after, order=order
                )
                for i in response["data"]:
                    all_items.append(i)
                after = response["list_metadata"]["after"]
            return all_items

        else:
            raise ValueError("Invalid list type")
