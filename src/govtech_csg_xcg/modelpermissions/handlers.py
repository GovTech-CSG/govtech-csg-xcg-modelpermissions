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
from crum import get_current_user
from django.conf import settings
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from guardian.utils import get_anonymous_user

from govtech_csg_xcg.modelpermissions import logger

from . import scope
from .exceptions import RbacPermissionDenied
from .shortcuts import get_model_permissions, with_sudo
from .signals import post_read, pre_update


def permission_check_required(model) -> bool:
    """Determine whether permission check is required for the specified model
        by checking whether it has `xcg_rbac_permission_check` set

    Args:
        model: Django model class

    Returns:
        True if the model has `xcg_rbac_permission_check=True`
    """
    return getattr(model, "xcg_rbac_permission_check", False)


@receiver(pre_save)
@with_sudo
def handle_pre_save(sender, instance=None, **kwargs):  # pylint: disable=unused-argument
    """Handles the Django built-in `pre_save` signal

    Args:
        sender (models.Model class): the Django model class that sends the `pre_save` signal
        instance (models.Model, optional): the model instancee that sends along with the
            `pre_save` signal. Defaults to None.

    Raises:
        RbacPermissionDenied: Raise if the current logged in user doesn't have the required
            permission. Django will return 403 if not handled.
    """

    if scope.in_parent_scope(scope.SCOPE_RBAC_IGNORE):
        return

    if not permission_check_required(sender):
        return

    user = get_current_user()

    # django-guardian will create an Anonymous user if not logged in.
    # but during testing, django-crum might get None user if not logged in.
    # handle this case
    if user is None:
        user = get_anonymous_user()

    perms = get_model_permissions(sender)

    # pre_save send for object update:
    if instance and instance.pk and sender.objects.filter(pk=instance.pk).exists():
        instance_to_check = None
        if getattr(settings, "XCG_RBAC_OBJECT_CONTROL", True):
            instance_to_check = instance

        # `user.has_perm` will check for class permissions if `instance_to_check` is None.
        if not user.has_perm(perms["update"], instance_to_check):
            logger.error("user %s not allowed to update %s", user, instance)
            if getattr(settings, "XCG_RBAC_BLOCK", True):
                raise RbacPermissionDenied(
                    f"user {user} not allowed to update {instance}"
                )
    else:
        # pre_save send for object creation
        if not user.has_perm(perms["create"]):
            logger.error("user %s not allowed to create %s object", user, sender)
            if getattr(settings, "XCG_RBAC_BLOCK", True):
                raise RbacPermissionDenied(
                    f" user {user} not allowed to create {sender} object"
                )


@receiver(pre_delete)
@with_sudo
def handle_pre_delete(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Handles the Django built-in `pre_delete` signal

    Args:
        sender (models.Model class): the Django model class that sends the `pre_delete` signal
        instance (models.Model): the model instance to be deleted.

    Raises:
        RbacPermissionDenied: Raise if the current logged in user doesn't have the required
            permission. Django will return 403 if not handled.
    """

    if scope.in_parent_scope(scope.SCOPE_RBAC_IGNORE):
        return

    if not permission_check_required(sender):
        return

    user = get_current_user()
    if user is None:
        user = get_anonymous_user()

    perms = get_model_permissions(sender)

    instance_to_check = None
    if getattr(settings, "XCG_RBAC_OBJECT_CONTROL", True):
        instance_to_check = instance

    if not user.has_perm(perms["delete"], instance_to_check):
        logger.error("user %s not allowed to delete %s", user, instance)
        if getattr(settings, "XCG_RBAC_BLOCK", True):
            raise RbacPermissionDenied(f"user {user} not allowed to delete {instance}")


@receiver(post_read)
@with_sudo
def handle_post_read(sender, queryset, **kwargs):  # pylint: disable=unused-argument
    """Handles the xcg extended `post_read` signal. `post_read` signal will be sent after user
        has evaluated a queryset, check this for when querysets are evaluated:
        https://docs.djangoproject.com/en/4.1/ref/models/querysets/#when-querysets-are-evaluated

    Args:
        sender (models.Model class): the Django model class that sends the `post_read` signal
        queryset (models.QuerySet): the queryset instance that will be returned to the user

    Raises:
        RbacPermissionDenied: Raise if the current logged in user doesn't have the required
            permission. Django will return 403 if not handled.
    """

    if scope.in_parent_scope(scope.SCOPE_RBAC_IGNORE):
        return

    if not permission_check_required(sender):
        return

    user = get_current_user()
    if user is None:
        user = get_anonymous_user()

    perms = get_model_permissions(sender)

    if not getattr(settings, "XCG_RBAC_OBJECT_CONTROL", True):
        if user.has_perm(perms["read"]):
            return
        # try to use the `queryset._result_cache` within the permission check so that the
        # queryset will not be evaluated once more
        # pylint: disable-next=protected-access
        logger.error("user %s not allowed to read %s", user, queryset._result_cache)
        if getattr(settings, "XCG_RBAC_BLOCK", True):
            # pylint: disable-next=protected-access
            raise RbacPermissionDenied(
                f"user {user} not allowed to read {queryset._result_cache}"
            )
        return

    # pylint: disable-next=protected-access
    if not all(user.has_perm(perms["read"], ins) for ins in queryset._result_cache):
        logger.warning(
            "user %s doesn't have enough permission to see all objects in this queryset %s",
            user,
            queryset._result_cache,  # pylint: disable=protected-access
        )
        # pylint: disable-next=protected-access
        logger.error("user %s not allowed to read %s", user, queryset._result_cache)
        if getattr(settings, "XCG_RBAC_BLOCK", True):
            # pylint: disable-next=protected-access
            raise RbacPermissionDenied(
                f"user {user} not allowed to read {queryset._result_cache}"
            )


@receiver(pre_update)
@with_sudo
def handle_pre_update(sender, queryset, **kwargs):  # pylint: disable=unused-argument
    """Handles the xcg extended `pre_update` signal. `pre_update` signal will be sent before
        updating records using `QuerySet.update()`.

    Args:
        sender (models.Model class): the Django model class that sends the `pre_update` signal
        queryset (models.QuerySet): the queryset instance that will be updated

    Raises:
        RbacPermissionDenied: Raise if the current logged in user doesn't have the required
            permission. Django will return 403 if not handled.
    """

    if scope.in_parent_scope(scope.SCOPE_RBAC_IGNORE):
        return

    if not permission_check_required(sender):
        return

    user = get_current_user()
    if user is None:
        user = get_anonymous_user()

    perms = get_model_permissions(sender)

    # per-model control
    if not getattr(settings, "XCG_RBAC_OBJECT_CONTROL", True):
        if user.has_perm(perms["update"]):
            return
        # pylint: disable-next=protected-access
        logger.error("user %s not allowed to update %s", user, queryset._result_cache)
        if getattr(settings, "XCG_RBAC_BLOCK", True):
            raise RbacPermissionDenied(
                # pylint: disable-next=protected-access
                f"user {user} not allowed to update {queryset._result_cache}"
            )
        return

    # per-object control
    if not all(user.has_perm(perms["update"], ins) for ins in queryset):
        # pylint: disable-next=protected-access
        logger.error("user %s not allowed to update %s", user, queryset._result_cache)
        if getattr(settings, "XCG_RBAC_BLOCK", True):
            raise RbacPermissionDenied(
                # pylint: disable-next=protected-access
                f"user {user} not allowed to update {queryset._result_cache}"
            )
