# main/accounts/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import render, resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from employees import models as employees_models

from accounts import forms as accounts_forms
from accounts.tokens import account_activation_token
from main.utils import generate_random_email

UserModel = get_user_model()


def activate_view(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(
            request,
            template_name="accounts/account_activated.html",
            context={"user": user},
        )
    else:
        return render(request, "accounts/invalid_activation.html")


class SignUpViewNopassword(CreateView):
    form_class = accounts_forms.CustomUserCreationFormNopassword
    success_url = reverse_lazy("accounts:login_no_password")
    template_name = "registration/signup-nopassword.html"

    def form_valid(self, form):
        employee_id = form.cleaned_data.get("employee_id")
        emp_obj = employees_models.EmployeeModel.objects.filter(
            employee_id=employee_id
        ).first()
        user = UserModel.objects.filter(username=str(employee_id)).first()
        if not user:
            user = form.save(commit=False)
            user.username = str(employee_id)
            user.emp_id_obj = emp_obj
            user.email = generate_random_email(name=employee_id)
            user.is_active = True
            user.is_no_password = True
            user.preferred_name = emp_obj.name
            user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            "Invalid form submission. Please check your input.",
        )
        return super().form_invalid(form)


class SignUpView(CreateView):
    form_class = accounts_forms.CustomUserCreationForm
    success_url = reverse_lazy("accounts:signup_done")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        self.send_email(user, form)
        return super().form_valid(form)

    def send_email(self, user, form):
        mail_subject = "[MLRS] Activation link for new MLRS account"
        message = render_to_string(
            "accounts/activation_email.txt",
            {
                "user": user,
                "domain": self.request.get_host(),
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        to_email = form.cleaned_data.get("email")
        email = EmailMessage(mail_subject, message, to=[to_email])
        try:
            email.send(fail_silently=False)
            messages.add_message(
                self.request, messages.INFO, f"Email sent successfully to {to_email}"
            )
        except Exception as e:
            messages.add_message(self.request, messages.ERROR, "Email sending failed.")
            messages.add_message(self.request, messages.ERROR, f"{e}. Please contact the administrator ({settings.ADMIN_EMAIL}).")


class SignUpConfirmView(TemplateView):
    template_name = "accounts/signup_confirm.html"


class CustomLoginView(LoginView):
    authentication_form = accounts_forms.CustomUserLoginForm


class CustomLoginViewNopassword(LoginView):
    authentication_form = accounts_forms.CustomUserLoginFormNopassword
    template_name = "registration/login-no-password.html"


class CustomUserListView(LoginRequiredMixin, ListView):
    model = UserModel
    template_name = "accounts/users_list.html"
    context_object_name = "objects"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user_obj_list = [obj for obj in context["objects"]]
        objects = []
        for user_obj in user_obj_list:
            if user_obj.username == "admin":
                continue
            data = {
                "user_obj": user_obj,
                "is_operator": user_obj.has_perm("accounts.is_operator"),
                "is_engineer": user_obj.has_perm("accounts.is_engineer"),
                "is_approver": user_obj.has_perm("accounts.is_approver"),
                "is_endorser": user_obj.has_perm("accounts.is_endorser"),
            }
            objects.append(data)
        context["objects"] = objects
        return context


class CustomUserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = UserModel
    form_class = accounts_forms.CustomUserChangeForm
    template_name = "accounts/update_user.html"
    context_object_name = "objects"
    success_url = reverse_lazy("accounts:users_list")
    permission_required = ["accounts.is_engineer"]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context


class CustomUserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserModel
    form_class = accounts_forms.CustomUserProfileForm
    template_name = "accounts/user_profile.html"
    context_object_name = "objects"
    success_url = reverse_lazy("landingpage")
