class WorkOSBaseResource(object):
    """Representation of a WorkOS Resource as returned through the API.

    Attributes:
        OBJECT_FIELDS (list): List of fields a Resource is comprised of.
    """

    OBJECT_FIELDS = []

    @classmethod
    def construct_from_response(cls, response):
        """Returns an instance of WorkOSBaseResource.

        Args:
            response (dict): Resource data from a WorkOS API response

        Returns:
            WorkOSBaseResource: Instance of a WorkOSBaseResource with OBJECT_FIELDS fields set
        """
        obj = cls()
        for field in cls.OBJECT_FIELDS:
            setattr(obj, field, response.get(field))

        return obj

    def to_dict(self):
        """Returns a dict representation of the WorkOSBaseResource.

        Returns:
            dict: A dict representation of the WorkOSBaseResource
        """
        obj_dict = {}
        for field in self.OBJECT_FIELDS:
            obj_dict[field] = getattr(self, field, None)

        return obj_dict
