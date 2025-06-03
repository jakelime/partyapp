from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if email:
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
    emp_id_obj = models.ForeignKey(
        "employees.EmployeeModel",
        on_delete=models.SET_NULL,
        null=True,
        # related_name="%(app_label)s_%(class)s_emp_id_obj",
    )
    email = models.EmailField(blank=True, null=True, unique=True)
    is_no_password = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("is_admin", "Administrator level access"),
            ("is_gamemaster", "Game Master level access"),
        )

    def __str__(self):
        if self.username is None:
            return f"none-{self.pk}"
        else:
            return str(self.emp_id_obj)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def get_edit_url(self):
        return reverse_lazy("accounts:user_update", kwargs={"pk": self.pk})

    def get_profile_url(self):
        return reverse_lazy("accounts:update_profile", kwargs={"pk": self.pk})

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
