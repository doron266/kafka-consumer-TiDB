from django.urls import path
from . import views

urlpatterns = [
    # Users
    path("users", views.get_users, name="get_users"),
    path("users/add", views.add_user, name="add_user"),
    path("users/update", views.update_user, name="update_user"),
    path("users/delete", views.delete_user, name="delete_user"),

    # Logins
    path("logins", views.get_logins, name="get_logins"),
    path("logins/add", views.add_login, name="add_login"),
    path("logins/delete", views.delete_logins_by_email, name="delete_logins_by_email"),
]
