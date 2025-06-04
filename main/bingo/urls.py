# main/bingo/urls.py
from django.urls import path

from . import views

app_name = "bingo"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("player", views.PlayerView.as_view(), name="player"),
    path("gmview", views.GameMasterView.as_view(), name="gmview"),
    path(
    'gmview/<int:period>/<str:toggle_state>/',
    views.GameMasterView.as_view(),
    name='game_master_with_params'
    ),
    path("settings", views.SettingsView.as_view(), name="settings"),
]
