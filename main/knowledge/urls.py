# main/knowledge/urls.py
from django.urls import path

from . import views

app_name = "knowledge"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("player", views.SubmitAnswerView.as_view(), name="player")
]
