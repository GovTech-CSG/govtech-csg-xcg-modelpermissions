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
from django.conf import settings
from django.shortcuts import render

from .exceptions import RbacPermissionDenied


class ModelPermissionsMiddleware:
    """Role based access control middleware, this middleware mostly for handling the
    `RbacPermissionDenied` exceptions raised and return a specified error page.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        """Handle the `RbacPermissionDenied` raised by the permission checks."""
        if isinstance(exception, RbacPermissionDenied):
            template_name = getattr(settings, "XCG_RBAC_403_TEMPLATE", None)
            if not template_name:
                raise exception

            return render(
                request=request,
                template_name=template_name,
                status=403,
                context={"errmsg": exception.__str__},
            )

        return None
