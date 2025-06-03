# main/bingo/urls.py
from django.urls import path

from . import views

app_name = "bingo"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("player/<int:pk>", views.PlayerView.as_view(), name="player"),
    path("test", views.TestView.as_view(), name="test"),
]
