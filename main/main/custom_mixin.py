# main/main/custom_mixin.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def get_login_url(self):
        return reverse_lazy("accounts:login")


class LoginRequiredMixinNopassword(LoginRequiredMixin):
    def get_login_url(self):
        return reverse_lazy("accounts:login_no_password")
