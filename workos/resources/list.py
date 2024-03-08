from workos.resources.base import WorkOSBaseResource
from warnings import warn


class WorkOSListResource(WorkOSBaseResource):
    """Representation of a WorkOS List Resource as returned through the API.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSListResource is comprised of.
    """

    OBJECT_FIELDS = ["data", "list_metadata", "metadata"]

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
        """
        This function returns the entire list of items when there are more than 100 unless a limit has been specified.
        """
        data_dict = self.to_dict()
        data = data_dict["data"]
        after = data_dict["list_metadata"]["after"]
        before = data_dict["list_metadata"]["before"]
        method = data_dict["metadata"]["method"]
        order = data_dict["metadata"]["params"]["order"]

        keys_to_remove = ["after", "before"]
        resource_specific_params = {
            k: v
            for k, v in self.to_dict()["metadata"]["params"].items()
            if k not in keys_to_remove
        }

        if "default_limit" not in resource_specific_params:
            if len(data) == resource_specific_params["limit"]:
                yield data
                return
        else:
            del resource_specific_params["default_limit"]

            if before is None:
                next_page_marker = after
                string_direction = "after"
            else:
                order = None
                next_page_marker = before
                string_direction = "before"

            params = {
                "after": after,
                "before": before,
                "order": order or "desc",
            }
            params.update(resource_specific_params)

            params = {k: v for k, v in params.items() if v is not None}

            while next_page_marker is not None:
                response = method(self, **params)
                if type(response) != dict:
                    response = response.to_dict()
                for i in response["data"]:
                    data.append(i)
                next_page_marker = response["list_metadata"][string_direction]
                yield data
                data = []
