from enum import Enum


class Order(Enum):
    Asc = "asc"
    Desc = "desc"


class Type(Enum):
    Directories = "directories"
    DirectoryUsers = "directory_users"
    DirectoryGroups = "directory_groups"
    Organizations = "organizations"
    Connections = "connections"
