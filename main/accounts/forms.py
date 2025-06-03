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
from django.views.decorators.debug import sensitive_variables
from employees import models as employees_models

from accounts import models as accounts_models
from main.utils import get_datetime_str

UserModel = get_user_model()


class CustomUserLoginFormNopassword(AuthenticationForm):

    username = forms.CharField(
        required=True,
        label="Username or Employee ID",
    )
    helper = FormHelper()
    helper.layout = Layout(
        FloatingField("username"),
        FormActions(
            Submit("submit", "Login", css_class="btn-primary btn-lg"),
        ),
    )

    @sensitive_variables()
    def clean(self):
        password = self.cleaned_data.get("password")
        if not password:
            self.cleaned_data["password"] = settings.DEFAULT_USER_PASSWORD
        super().clean()


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
        cleaned_data = super().clean()
        employee_id = cleaned_data.get("employee_id")
        emp_obj = employees_models.EmployeeModel.objects.filter(
            employee_id=employee_id
        ).first()
        if not emp_obj:
            raise forms.ValidationError(
                f"Employee with ID {employee_id} does not exist!"
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
