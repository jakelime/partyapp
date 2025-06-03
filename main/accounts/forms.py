# accounts/forms.py
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_variables
from employees import models as employees_models

from accounts import models as accounts_models
from main.utils import get_datetime_str

UserModel = get_user_model()


class AuthenticationFormNopassword(forms.Form):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True}))

    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        username_max_length = self.username_field.max_length or 254
        self.fields["username"].max_length = username_max_length
        self.fields["username"].widget.attrs["maxlength"] = username_max_length
        if self.fields["username"].label is None:
            self.fields["username"].label = capfirst(self.username_field.verbose_name)

    @sensitive_variables()
    def clean(self):
        self.cleaned_data["password"] = settings.DEFAULT_USER_PASSWORD
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = UserModel.objects.filter(username=username).first()
            print(f"{self.user_cache=}")
            if not self.user_cache.is_no_password:
                raise self.get_invalid_login_error()
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
                print(f"login is allowed for {self.user_cache}")

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"username": self.username_field.verbose_name},
        )


class CustomUserLoginFormNopassword(AuthenticationFormNopassword):

    username = forms.CharField(
        required=True,
        label="Username or Employee ID",
    )
    password = forms.CharField(
        required=False,
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    helper = FormHelper()
    helper.layout = Layout(
        FloatingField("username"),
        FormActions(
            Submit("submit", "Login", css_class="btn-primary btn-lg"),
        ),
    )

    class Meta:
        model = UserModel
        fields = ("employee_id",)


class CustomUserCreationFormNopassword(forms.ModelForm):
    employee_id = forms.CharField(
        required=False,
        label="Employee ID",
        help_text="Example: 7xxxxxxx (8 characters)",
    )
    helper = FormHelper()
    helper.form_class = "form-horizontal"
    helper.layout = Layout(
        FloatingField("employee_id"),
        FormActions(
            Submit("submit", "Register as new user", css_class="btn-primary btn-lg"),
        ),
    )

    class Meta:
        model = accounts_models.CustomUser
        fields = ("employee_id",)

    def clean(self):
        """this method will check if employee_id exists in EmployeeModel"""
        cleaned_data = super().clean()
        employee_id = cleaned_data.get("employee_id")
        emp_obj = employees_models.EmployeeModel.objects.filter(
            employee_id=employee_id
        ).first()
        if not emp_obj:
            raise forms.ValidationError(
                f"Employee with ID {employee_id} does not exist!"
            )
        user = UserModel.objects.filter(emp_id_obj=emp_obj).first()
        if user:
            raise forms.ValidationError(
                f"User with Employee ID {employee_id} already exists!"
            )
        return cleaned_data


class CustomUserLoginForm(AuthenticationForm):
    ## AuthenticationForm inherits NOT from forms.ModelForm! but forms.Form
    username = forms.CharField(
        required=True,
        label="Username or Email",
        # widget=forms.EmailInput(
        #     attrs={"placeholder": f"user.name@{settings.[0]}"}
        # ),
    )
    helper = FormHelper()
    # helper.form_class = "form-horizontal"
    helper.layout = Layout(
        FloatingField("username"),
        FloatingField("password"),
        FormActions(
            Submit("submit", "Login", css_class="btn-primary btn-lg"),
        ),
    )

    def clean(self):
        super().clean()
        print(f"{self.cleaned_data=}")
        return self.cleaned_data


class CustomUserCreationForm(UserCreationForm):
    # AuthenticationForm inherits from forms.ModelForm,
    # high level and allows crispy form
    username = forms.CharField(
        required=True, label="Username", help_text="Example: john.doe"
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Example: user.name@email.com",
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
        model = accounts_models.CustomUser
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"]
        email_username, email_domain = email.split("@")
        return email

    def clean(self) -> dict:
        cleaned_data = super().clean()
        username = self.cleaned_data["username"]
        if UserModel.objects.filter(username=username).exists():
            username, _ = cleaned_data["email"].split("@")
        if UserModel.objects.filter(username=username).exists():
            username = f"{username}_{get_datetime_str()}"
        cleaned_data["username"] = username
        return cleaned_data


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
        model = accounts_models.CustomUser
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
        email_is_verified = self.fields.get("email_is_verified")
        if email_is_verified:
            email_is_verified.disabled = True
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
        model = accounts_models.CustomUser
        fields = ("email", "username", "preferred_name", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        username = self.fields.get("username")
        if username:
            username.disabled = True
