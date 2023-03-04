import workos
from workos.utils.pagination_order import Order, Type


def timestamp_compare(timestamp_0, timestamp_1):
    if timestamp_0 < timestamp_1:
        return Order.Asc
    else:
        return Order.Desc


def get_response(type, after=None, before=None, order=None, parent_resource_id=None):
    params = {"before": before, "after": after, "order": order, "limit": 100}
    if parent_resource_id:
        params["directory"] = parent_resource_id

    if type == Type.Directories:
        response = workos.client.directory_sync.list_directories(**params)
        return response
    if type == Type.DirectoryUsers:
        response = workos.client.directory_sync.list_users(**params)
        return response
    if type == Type.DirectoryGroups:
        response = workos.client.directory_sync.list_groups(**params)
        return response
    if type == Type.Organizations:
        response = workos.client.organizations.list_organizations(**params)
        return response
    if type == Type.Connections:
        response = workos.client.sso.list_connections(**params)
        return response
