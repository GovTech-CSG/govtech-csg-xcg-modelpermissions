from .settings_object_level import *  # noqa: F401, F403

MIDDLEWARE += [  # noqa: F405
    "govtech_csg_xcg.modelpermissions.middleware.ModelPermissionsMiddleware"
]

XCG_RBAC_403_TEMPLATE = "custom_403.html"
