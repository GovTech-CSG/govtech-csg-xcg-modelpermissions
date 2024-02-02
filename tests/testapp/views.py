"""Views for automated testing of the modelpermissions package.

Note that the views will not work without setting up the test fixtures (i.e. TestCase.setUp()).
"""
from crum import impersonate
from django.contrib.auth.models import User
from django.http import HttpResponse

from govtech_csg_xcg.modelpermissions.shortcuts import sudo, with_sudo

from .models import Person


# =================================================================
# Views for testing object and model level permissions enforcement
# =================================================================
def create_person(request):
    """Create permissions are only applicable for model-level permissions."""
    Person(name="new_person").save()
    return HttpResponse("New person created")


def read_person(request):
    Person.objects.get(name="existing_person")
    return HttpResponse("Existing person retrieved from DB")


def update_person(request):
    super_user = User.objects.get(username="test_superuser")
    with impersonate(super_user):
        person = Person.objects.get(name="existing_person")
    person.name = "another_person"
    person.save()
    return HttpResponse(
        "Person named existing_person updated to be called another_person"
    )


def delete_person(request):
    super_user = User.objects.get(username="test_superuser")
    with impersonate(super_user):
        person = Person.objects.get(name="existing_person")
    person.delete()
    return HttpResponse("Person named existing_person deleted")


# ============================================
# Views for testing the "sudo" context manager
# ============================================
def create_person_sudo(request):
    """Only for model-level permissions."""
    with sudo():
        return create_person(request)


def read_person_sudo(request):
    with sudo():
        return read_person(request)


def update_person_sudo(request):
    with sudo():
        person = Person.objects.get(name="existing_person")
        person.name = "another_person"
        person.save()
    return HttpResponse(
        "Person named existing_person updated to be called another_person"
    )


def delete_person_sudo(request):
    with sudo():
        person = Person.objects.get(name="existing_person")
        person.delete()
    return HttpResponse("Person named existing_person deleted")


# ===========================================
# Views for testing the "with_sudo" decorator
# ===========================================
@with_sudo
def create_person_with_sudo(request):
    """Only for model-level permissions."""
    return create_person(request)


@with_sudo
def read_person_with_sudo(request):
    return read_person(request)


@with_sudo
def update_person_with_sudo(request):
    person = Person.objects.get(name="existing_person")
    person.name = "another_person"
    person.save()
    return HttpResponse(
        "Person named existing_person updated to be called another_person"
    )


@with_sudo
def delete_person_with_sudo(request):
    person = Person.objects.get(name="existing_person")
    person.delete()
    return HttpResponse("Person named existing_person deleted")
