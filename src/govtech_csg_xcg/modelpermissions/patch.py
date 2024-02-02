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
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save

from . import scope
from .signals import post_read, pre_update


def do_patch():
    """Monkey-patch QuerySet methods to inject additional
    permission control
    """
    QuerySet.bulk_create = new_bulk_create
    QuerySet._fetch_all = new_fetch_all  # pylint: disable=protected-access
    QuerySet.update = new_update


# CREATE

# bulk_create() will not send `pre_save`, patch it to let it send `pre_save`
# with a list of objects to be created
orig_bulk_create = QuerySet.bulk_create


def new_bulk_create(self, *args, **kwags):
    """Patched QuerySet.bulk_create() function that will send an extra `pre_save`
        signal with a list of objects to be created.

    Returns:
        List[_T@QuerySet]
    """
    if not scope.in_scope(scope.SCOPE_RBAC_IGNORE):
        pre_save.send(sender=self.model)
    return orig_bulk_create(self, *args, **kwags)


# READ

# `QuerySet._fetch_all()` will be called when django evaluate the querys,
# i.e. read data from db
# patch `QuerySet._fetch_all()` function to check on read permission.
orig_fetch_all = QuerySet._fetch_all  # pylint: disable=protected-access


def new_fetch_all(self, *args, **kwags):
    """Patched `QuerySet._fetch_all()` function that will send an extra `post_read`
    signal with a list of objects to be returned to the user.
    """
    orig_fetch_all(self, *args, **kwags)
    if not scope.in_scope(scope.SCOPE_RBAC_IGNORE):
        post_read.send(sender=self.model, queryset=self)


# UPDATE

# QuerySet.update() will not send `pre_save` signal. Monkey-patch it so that we
# can inject permission control.
orig_update = QuerySet.update


def new_update(self, *args, **kwags):
    """Patched `QuerySet.update()` function that will send an extra `pre_update`
    signal with a list of objects to be updated.
    """
    # NOTE that the queryset is not evaluated (django not retrive it from db yet)
    # prior to update, insted it will be directly executed, this means the queryset
    # will be evaluated first to get the objects to be updated, by checking the
    # content of the queryset.
    if not scope.in_scope(scope.SCOPE_RBAC_IGNORE):
        pre_update.send(sender=self.model, queryset=self)
    rows = orig_update(self, *args, **kwags)
    return rows
