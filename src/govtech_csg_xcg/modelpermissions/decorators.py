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
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def orm_default_permissions_check(original_class):
    """decorator Django models, which will mark the model
    as require the permission check"""
    if not issubclass(original_class, models.Model):
        raise ImproperlyConfigured(
            f"This decorator can \
            only be used on Django models instead of {original_class}"
        )

    original_class.xcg_rbac_permission_check = True
    return original_class
