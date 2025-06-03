# controls/urls.py
from django.urls import path

from . import views

app_name = "controls"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("users", views.UserListView.as_view(), name="users_list_view"),
]
