import logging
import os
from unittest import skipIf, skipUnless

from crum import impersonate
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from govtech_csg_xcg.modelpermissions.shortcuts import (
    assign_perm,
    get_model_permissions,
)

from .models import Person

SETTINGS_NAME = None
settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
if settings_module == "testproject.settings_object_level":
    SETTINGS_NAME = "object"
elif settings_module == "testproject.settings_model_level":
    SETTINGS_NAME = "model"
elif settings_module == "testproject.settings_custom_403":
    SETTINGS_NAME = "custom_403"

logging.getLogger("modelpermissions").setLevel(logging.CRITICAL)


class TestModelPermissions(TestCase):
    """Test case for the govtech-csg-xcg-modelpermissions package."""

    @classmethod
    def setUpTestData(cls):
        # Create a super user whom we will use to set up our per-method test fixture.
        # We use crum's "impersonate" feature rather than sudo or with_sudo
        # because we need to test the latter, which are features of our package,
        # whereas "impersonate" is a feature of crum, which is outside of our test scope.
        # We create the super user at the class level to avoid re-creating before each test method.
        cls.super_user = User.objects.create_superuser(
            username="test_superuser", password="password"
        )

    def setUp(self):
        # Unlike the super user, this test user is created here so that we don't
        # have to manually delete permissions after each test method.
        self.user = User.objects.create_user(username="test_user", password="password")
        self.client.login(username="test_user", password="password")
        with impersonate(self.super_user):
            self.instance = Person(name="existing_person")
            self.instance.save()

    @parameterized.expand(
        [
            ("read",),
            ("update",),
            ("delete",),
        ]
    )
    @skipUnless(SETTINGS_NAME == "object", "")
    def test_user_with_object_level_permission_allowed_to_perform_specified_action(
        self, action
    ):
        perms = get_model_permissions(Person)
        assign_perm(perms[action], self.user, self.instance)
        response = self.client.get(reverse(action))
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(
        [
            ("read", "create"),
            ("read", "update"),
            ("read", "delete"),
            ("update", "create"),
            ("update", "read"),
            ("update", "delete"),
            ("delete", "create"),
            ("delete", "read"),
            ("delete", "update"),
        ]
    )
    @skipUnless(SETTINGS_NAME == "object", "")
    def test_user_without_object_level_permission_cannot_perform_specified_action(
        self, allowed_action, target_action
    ):
        perms = get_model_permissions(Person)
        assign_perm(perms[allowed_action], self.user, self.instance)
        response = self.client.get(reverse(target_action))
        self.assertEqual(response.status_code, 403)

    # NOTE: The Django authorization system's built-in permissions use the
    # terms 'add' instead of 'create', 'view' instead of 'read', and 'change' instead of 'update'.
    # See https://docs.djangoproject.com/en/stable/topics/auth/default/#default-permissions
    @parameterized.expand(
        [
            ("add", "create"),
            ("view", "read"),
            ("change", "update"),
            ("delete", "delete"),
        ]
    )
    @skipUnless(SETTINGS_NAME == "model", "")
    def test_user_with_model_level_permission_allowed_to_perform_specified_action(
        self, django_action_name, generic_action_name
    ):
        perm = Permission.objects.get(codename=f"{django_action_name}_person")
        self.user.user_permissions.add(perm)
        response = self.client.get(reverse(generic_action_name))
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(
        [
            ("add", "read"),
            ("add", "update"),
            ("add", "delete"),
            ("view", "create"),
            ("view", "update"),
            ("view", "delete"),
            ("change", "create"),
            ("change", "read"),
            ("change", "delete"),
            ("delete", "create"),
            ("delete", "read"),
            ("delete", "update"),
        ]
    )
    @skipUnless(SETTINGS_NAME == "model", "")
    def test_user_without_model_level_permission_cannot_perform_specified_action(
        self, allowed_django_action, target_generic_action
    ):
        perm = Permission.objects.get(codename=f"{allowed_django_action}_person")
        self.user.user_permissions.add(perm)
        response = self.client.get(reverse(target_generic_action))
        self.assertEqual(response.status_code, 403)

    @parameterized.expand(
        [
            ("create-sudo",),
            ("create-with-sudo",),
            ("read-sudo",),
            ("read-with-sudo",),
            ("update-sudo",),
            ("update-with-sudo",),
            ("delete-sudo",),
            ("delete-with-sudo",),
        ]
    )
    # It's enough that we run this test for both model and object-level permissions checks,
    # so we skip these tests if the settings file used is meant for testing custom 403 template.
    @skipIf(SETTINGS_NAME == "custom_403", "")
    def test_sudo_allows_all_actions(self, sudo_view_name):
        # We don't assign any permissions here so as to check if "sudo" and "with_sudo" bypasses checks.
        response = self.client.get(reverse(sudo_view_name))
        self.assertEqual(response.status_code, 200)

    @skipUnless(SETTINGS_NAME == "custom_403", "")
    def test_custom_403_template_returned_when_model_permissions_middleware_activated_and_configured(
        self,
    ):
        response = self.client.get(reverse("read"))
        self.assertContains(
            response,
            text="This is a custom 403 template for model permissions",
            status_code=403,
        )
