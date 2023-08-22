from workos.resources.base import WorkOSBaseResource


class WorkOSUserOrganization(WorkOSBaseResource):
    """Contains the id and name of the associated Organization.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSUserOrganization comprises.
    """

    OBJECT_FIELDS = [
        "id",
        "name",
    ]


class WorkOSUnauthorizedOrganizationReason(WorkOSBaseResource):
    """Contains the id and name of the associated Organization.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSUnauthorizedOrganizationReason comprises.
    """

    OBJECT_FIELDS = [
        "type",
        "allowed_authentication_methods",
    ]


class WorkOSAuthorizedOrganization(WorkOSBaseResource):
    """Contains the id and name of the associated Organization.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSUserOrganization comprises.
    """

    @classmethod
    def construct_from_response(cls, response):
        authorized_organization = super(
            WorkOSAuthorizedOrganization, cls
        ).construct_from_response(response)

        organization = WorkOSUserOrganization.construct_from_response(
            response["organization"]
        )
        authorized_organization.organization = organization

        return authorized_organization

    def to_dict(self):
        authorized_organizations_dict = super(
            WorkOSAuthorizedOrganization, self
        ).to_dict()

        organization_dict = self.organization.to_dict()
        authorized_organizations_dict["organization"] = organization_dict

        return authorized_organizations_dict


class WorkOSUnauthorizedOrganization(WorkOSBaseResource):
    """Contains the unauthorized organization and reasons for the non authorization.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSUserOrganization comprises.
    """

    @classmethod
    def construct_from_response(cls, response):
        unauthorized_organization = super(
            WorkOSUnauthorizedOrganization, cls
        ).construct_from_response(response)

        organization = WorkOSUserOrganization.construct_from_response(
            response["organization"]
        )
        unauthorized_organization.organization = organization

        unauthorized_organization.reason = []

        for reason in response["reasons"]:
            reason = WorkOSUnauthorizedOrganizationReason.construct_from_response(
                reason
            )
            unauthorized_organization.reason.append(reason)

        return unauthorized_organization

    def to_dict(self):
        unauthorized_organizations_dict = super(
            WorkOSUnauthorizedOrganization, self
        ).to_dict()

        organization_dict = self.organization.to_dict()
        unauthorized_organizations_dict["organization"] = organization_dict

        unauthorized_organizations_dict["reasons"] = []

        for reason in self.reason:
            reason_dict = reason.to_dict()
            unauthorized_organizations_dict["reasons"].append(reason_dict)

        return unauthorized_organizations_dict


class WorkOSSession(WorkOSBaseResource):
    """Representation of a Session response as returned by WorkOS through User Management features.

    Attributes:
        OBJECT_FIELDS (list): List of fields a class WorkOSSession comprises.
    """

    OBJECT_FIELDS = [
        "id",
        "token",
        "created_at",
        "updated_at",
    ]

    @classmethod
    def construct_from_response(cls, response):
        session = super(WorkOSSession, cls).construct_from_response(response)

        session.authorized_organizations = []
        session.unauthorized_organizations = []

        for authorized_organization in response["authorized_organizations"]:
            authorized_organization = (
                WorkOSAuthorizedOrganization.construct_from_response(
                    authorized_organization
                )
            )
            session.authorized_organizations.append(authorized_organization)

        for unauthorized_organization in response["unauthorized_organizations"]:
            unauthorized_organization = (
                WorkOSUnauthorizedOrganization.construct_from_response(
                    unauthorized_organization
                )
            )
            session.unauthorized_organizations.append(unauthorized_organization)

        return session

    def to_dict(self):
        session_dict = super(WorkOSSession, self).to_dict()

        session_dict["authorized_organizations"] = []
        session_dict["unauthorized_organizations"] = []

        for organization in self.authorized_organizations:
            organization_dict = organization.to_dict()
            session_dict["authorized_organizations"].append(organization_dict)

        for organization in self.unauthorized_organizations:
            organization_dict = organization.to_dict()
            session_dict["unauthorized_organizations"].append(organization_dict)

        return session_dict
