# ------------------------------------------------------------------------
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# This file incorporates work covered by the following copyright:
#
# Copyright (c) 2023 Agency for Science, Technology and Research (A*STAR).
#   All rights reserved.
# Copyright (c) 2023 Government Technology Agency (GovTech).
#   All rights reserved.
# ------------------------------------------------------------------------
import sys
from functools import partial

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian import shortcuts as gshortcuts

from govtech_csg_xcg.modelpermissions import logger

from .scope import SCOPE_RBAC_IGNORE, scope, with_scope

__all__ = [  # noqa: F822
    "get_model_permissions",
    "assign_perm",
    "remove_perm",
    "get_perms",
    "get_user_perms",
    "get_group_perms",
    "get_perms_for_model",
    "get_users_with_perms",
    "get_groups_with_perms",
    "get_objects_for_user",
    "get_objects_for_group",
]

# decorator to disable permission check
with_sudo = partial(with_scope, name=SCOPE_RBAC_IGNORE)()

# context manager to disable permission check
sudo = partial(scope, name=SCOPE_RBAC_IGNORE)


def get_model_permissions(model):
    """Get the default permissions of a given model.

    Args:
        model: the Django model class

    Returns:
       A dictionary that stores the CRUD permissions of the model.
       For example:

       `{'create': add_permission,'read': view_permission,
       'update': change_permission,'delete': delete_permission}`
    """

    # get all the permissions related to the model
    content_type = ContentType.objects.get_for_model(model)
    all_permissions = Permission.objects.filter(content_type=content_type)
    app_label = model._meta.app_label  # pylint: disable=protected-access

    # try to identify the default permissions by the prefix of `Permission.codename`
    add_permission, delete_permission, change_permission, view_permission = (
        None,
        None,
        None,
        None,
    )
    for perm in all_permissions:
        codename = perm.codename
        if "add_" in codename:
            add_permission = ".".join([app_label, codename])
        elif "delete_" in codename:
            delete_permission = ".".join([app_label, codename])
        elif "change_" in codename:
            change_permission = ".".join([app_label, codename])
        elif "view_" in codename:
            view_permission = ".".join([app_label, codename])
        else:
            logger.warning("unknown permission: %s", perm)

    return {
        "create": add_permission,
        "read": view_permission,
        "update": change_permission,
        "delete": delete_permission,
    }


# commonly used shortcut functions provided by django-guardian
# instead of using the original guardian shortcuts, developers
# should use the decorated function provided by this module.
guardian_shortcuts = [
    gshortcuts.assign_perm,
    gshortcuts.remove_perm,
    gshortcuts.get_perms,
    gshortcuts.get_user_perms,
    gshortcuts.get_group_perms,
    gshortcuts.get_perms_for_model,
    gshortcuts.get_users_with_perms,
    gshortcuts.get_groups_with_perms,
    gshortcuts.get_objects_for_user,
    gshortcuts.get_objects_for_group,
]

# make the guardian shortcuts within the scope, i.e. no permission checks
# within these functions. Since these functions are not checked, developers
# should be more careful when using them.
for func in guardian_shortcuts:
    thismodule = sys.modules[__name__]
    # keep the original names of guardian shortcuts
    setattr(thismodule, func.__name__, with_sudo(func))
