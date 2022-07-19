from workos.resources.base import WorkOSBaseResource


class WorkOSPasswordlessSession(WorkOSBaseResource):
    """Representation of a Passwordless Session Response as returned by WorkOS through the Magic Link feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSPasswordlessSession is comprised of.
    """

    OBJECT_FIELDS = [
        "object",
        "id",
        "email",
        "expires_at",
        "link",
    ]

    @classmethod
    def construct_from_response(cls, response):
        create_session_response = super(
            WorkOSPasswordlessSession, cls
        ).construct_from_response(response)

        return create_session_response

    def to_dict(self):
        passwordless_session_response = super(WorkOSPasswordlessSession, self).to_dict()

        return passwordless_session_response
