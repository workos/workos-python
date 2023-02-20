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
        response = workos.client.directory_sync.list_users(
            directory=directory,
            limit=100,
            after=after,
            order=order,
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


def get_legacy_order_response(type, before, directory=None):
    if type == "directory":
        response = workos.client.directory_sync.list_directories(
            limit=100, before=before
        )
        return response
    if type == "directory_user":
        response = workos.client.directory_sync.list_users(
            directory=directory, limit=100, before=before
        )
        return response
    if type == "directory_group":
        response = workos.client.directory_sync.list_groups(
            directory=directory, limit=100, before=before
        )
        return response
    if type == "organization":
        response = workos.client.organizations.list_organizations(
            limit=100, before=before
        )
        return response
    if type == "connection":
        response = workos.client.sso.list_connections(limit=100, before=before)
        return response


def auto_paginate(list_type, all_items, after=None, before=None, directory=None):
    all_items = all_items
    after = after
    before = before

    if before is None:
        if len(all_items) > 1:
            order = timestamp_compare(
                all_items[0]["created_at"], all_items[len(all_items) - 1]["created_at"]
            )
        else:
            order = Order.Desc
    else:
        order = None

    if order is not None:
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

    if order is None:
        if directory is not None:
            while before is not None:
                response = get_legacy_order_response(list_type, before, directory)
                for i in response["data"]:
                    all_items.append(i)
                before = response["list_metadata"]["before"]
            return all_items
        while before is not None:
            response = get_legacy_order_response(list_type, before)
            for i in response["data"]:
                all_items.append(i)
            before = response["list_metadata"]["before"]
        return all_items
