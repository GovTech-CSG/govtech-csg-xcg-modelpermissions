from django.urls import path

from . import views

urlpatterns = [
    # Views for testing object and model-level permissions.
    path("create/", views.create_person, name="create"),
    path("read/", views.read_person, name="read"),
    path("update/", views.update_person, name="update"),
    path("delete/", views.delete_person, name="delete"),
    # Views for testing the sudo context manager.
    path("create_sudo/", views.create_person_sudo, name="create-sudo"),
    path("read_sudo/", views.read_person_sudo, name="read-sudo"),
    path("update_sudo/", views.update_person_sudo, name="update-sudo"),
    path("delete_sudo/", views.delete_person_sudo, name="delete-sudo"),
    # Views for testing the with_sudo decorator.
    path("create_with_sudo/", views.create_person_with_sudo, name="create-with-sudo"),
    path("read_with_sudo/", views.read_person_with_sudo, name="read-with-sudo"),
    path("update_with_sudo/", views.update_person_with_sudo, name="update-with-sudo"),
    path("delete_with_sudo/", views.delete_person_with_sudo, name="delete-with-sudo"),
]
