from enum import Enum


class Type(Enum):
    """
    Types of WorkOS List Resources

    Members:
    Directories: Used with List Directories
    DirectoryUsers: Used with List Directory Users
    DirectoryGroups: Used with List Directory Groups
    Organizations: Used with List Organizations
    Connections: Used with List Connections

    """

    Directories = "directories"
    DirectoryUsers = "directory_users"
    DirectoryGroups = "directory_groups"
    Organizations = "organizations"
    Connections = "connections"


class ParentResourceType(Enum):
    """
    Types of parent resource ID's that can be used to filter the list results. Some types can only be used with certain lists.

    Members:
    Directory: The directory ID, used with List Directory Users or List Directory Groups.
    Group: The directory group ID, used with List Directory Users.
    User: The ID of a WorkOS directory user, used only with List Directory Groups.
    Domains: An array of string domains, used only with List Organizations.
    Domain: A string domain, used with List Directories and List Connections.
    Search: Searchable string text to match against Directory names, used only with List Directories.
    ConnectionType: The connection ID, used with List Connections.
    OrganizationId: The organization ID, used only with List Connections.
    Organization: The organization ID, used only with List Directories.
    """

    Directory = "directory"
    Group = "group"
    User = "user"
    Domains = "domains"
    Domain = "domain"
    Search = "search"
    ConnectionType = "connection_type"
    OrganizationId = "organization_id"
    Organization = "organization"
