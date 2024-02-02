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
from django.apps import AppConfig

from .patch import do_patch


class ModelPermissionsConfig(AppConfig):
    """rbac app configuration"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "govtech_csg_xcg.modelpermissions"

    def ready(self):
        """Initialization function of `modelpermissions` app, it will patch
        critical functions"""

        do_patch()
        # import the signal handlers will enable them
        from . import handlers  # noqa: F401
