# accounts/urls.py
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.CustomUserListView.as_view(), name="users_list"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("signup-no-password/", views.SignUpViewNopassword.as_view(), name="signup_no_password"),
    path("signup_done/", views.SignUpConfirmView.as_view(), name="signup_done"),
    path("activate/<str:uidb64>/<str:token>", views.activate_view, name="activate"),
    path("login/", views.CustomLoginView.as_view()),
    path("login-no-password/", views.CustomLoginViewNopassword.as_view(), name="login_no_password"),
    path("users/<int:pk>", views.CustomUserUpdateView.as_view(), name="user_update"),
    path(
        "update_profile/<int:pk>",
        views.CustomUserProfileUpdateView.as_view(),
        name="update_profile",
    ),
]
