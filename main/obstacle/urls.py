# main/obstacle/urls.py
from django.urls import path

from . import views

app_name = "obstacle"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
