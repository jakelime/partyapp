from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy

from .customvalidators import WhitelistEmailValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(gettext_lazy("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(gettext_lazy("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(gettext_lazy("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    first_name = models.CharField(blank=True, max_length=32)
    last_name = models.CharField(blank=True, max_length=32)
    preferred_name = models.CharField(blank=True, max_length=64)
    username = models.CharField(max_length=32, blank=True, null=True, unique=True)
    email = models.EmailField(
        unique=True,
        # validators=[WhitelistEmailValidator(allowlist=settings.ALLOWED_EMAIL_DOMAINS)],
    )
    email_is_verified = models.BooleanField(default=False)

    password = models.CharField(_("password"), max_length=128, blank=True, null=True)

    class Meta:
        permissions = (("is_game_master", "Game Master"),)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.username:
            if not self.first_name:
                self.first_name = self.username.split(".")[0].capitalize()
            if not self.last_name:
                self.last_name = self.username.split(".")[-1].capitalize()
            if not self.preferred_name:
                self.preferred_name = (
                    f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
                )
        return super().save(*args, **kwargs)

    def get_edit_url(self):
        return reverse_lazy("accounts:user_update", kwargs={"pk": self.pk})

    def get_profile_url(self):
        return reverse_lazy("accounts:update_profile", kwargs={"pk": self.pk})

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        if password is not None:
            super().set_password(password)

    def has_password(self):
        return self.password is not None

    def check_password(self, raw_password):
        if not self.has_password():
            return False
        return super().check_password(raw_password)
