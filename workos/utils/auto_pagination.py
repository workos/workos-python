import workos
from workos.utils.pagination_order import Order


def timestamp_compare(timestamp_0, timestamp_1):
    if timestamp_0 < timestamp_1:
        return Order.Asc
    else:
        return Order.Desc


def get_response(type, after, order, directory=None):
    if type == "directory":
        response = workos.client.directory_sync.list_directories(
            limit=100, after=after, order=order
        )
        return response
    if type == "directory_user":
        response = workos.client.directory_sync.list_directories(
            limit=100, after=after, order=order
        )
        return response
    if type == "directory_group":
        response = workos.client.directory_sync.list_groups(
            directory=directory,
            limit=100,
            after=after,
            order=order,
        )
        return response
    if type == "organization":
        response = workos.client.organizations.list_organizations(
            limit=100, after=after, order=order
        )
        return response
    if type == "connection":
        response = workos.client.sso.list_connections(
            limit=100, after=after, order=order
        )
        return response


def auto_paginate(list_type, all_items, after, order, directory=None):
    all_items = all_items
    after = after
    if directory is not None:
        while after is not None:
            response = get_response(list_type, after, order, directory)
            for i in response["data"]:
                all_items.append(i)
            after = response["list_metadata"]["after"]
        return all_items
    while after is not None:
        response = get_response(list_type, after, order)
        for i in response["data"]:
            all_items.append(i)
        after = response["list_metadata"]["after"]
    return all_items
