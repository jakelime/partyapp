# accounts/forms.py
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.core import validators

from . import customvalidators
from .models import CustomUser

UserModel = get_user_model()


class CustomUserLoginForm(AuthenticationForm):
    ## AuthenticationForm inherits NOT from forms.ModelForm! but forms.Form
    username = forms.CharField(
        required=True,
        label="Username or Email",
    )
    helper = FormHelper()
    helper.layout = Layout(
        FloatingField("username"),
        FloatingField("password"),
        FormActions(
            Submit("submit", "Login", css_class="btn-primary btn-lg"),
        ),
    )


class CustomUserCreationForm(UserCreationForm):
    # AuthenticationForm inherits from forms.ModelForm,
    # high level and allows crispy form
    username = forms.CharField(
        required=True,
        label="Username",
        help_text="Example: john.doe. Lowercase letters, digits and _ only.",
        validators=[
            validators.RegexValidator(
                regex=r"^[a-z0-9_]+$",  # lowercase only
                message="Lowercase letters, digits and _ only! e.g. john.doe",
                code="invalid_username",
            ),
            validators.MinLengthValidator(
                4, "Username must be at least 4 characters long."
            ),
            customvalidators.validate_username_not_reserved,
            customvalidators.validate_username_unique,
        ],
    )
    email = forms.EmailField(
        required=True, label="Email", help_text="Example: john.doe@email.com"
    )
    helper = FormHelper()
    helper.form_class = "form-horizontal"
    helper.layout = Layout(
        FloatingField("username"),
        FloatingField("email"),
        FloatingField("password1"),
        FloatingField("password2"),
        FormActions(
            Submit("submit", "Register as new user", css_class="btn-primary btn-lg"),
        ),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


class CustomUserChangeForm(UserChangeForm):
    helper = FormHelper()
    helper.form_class = "form-horizontal"
    helper.layout = Layout(
        Field("email"),
        Field("username"),
        Field(
            "first_name",
        ),
        Field("last_name"),
        Field(
            "preferred_name",
        ),
        Field("groups"),
        Field("is_active"),
        FormActions(
            Submit("submit", "Save", css_class="btn-primary btn-lg"),
        ),
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "last_name",
            "preferred_name",
            "groups",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        username = self.fields.get("username")
        if username:
            username.disabled = True
        email = self.fields.get("email")
        if email:
            email.help_text = "Email id must be same as username!"


class CustomUserProfileForm(UserChangeForm):
    helper = FormHelper()
    helper.form_class = "form-horizontal"
    helper.layout = Layout(
        Field("email"),
        Field("username"),
        Field("preferred_name"),
        Field("first_name"),
        Field("last_name"),
        FormActions(
            Submit("submit", "Save", css_class="btn-primary btn-lg"),
        ),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username", "preferred_name", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        username = self.fields.get("username")
        if username:
            username.disabled = True
