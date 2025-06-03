# main/employees/urls.py
from django.urls import path

from . import views

app_name = "employees"
urlpatterns = [
    path("detail/<int:pk>", views.EmployeeDetailView.as_view(), name="detail_view"),
    path("create", views.EmployeeCreateView.as_view(), name="create_view"),
    path("", views.EmployeeCreateView.as_view(), name="home"),
]
