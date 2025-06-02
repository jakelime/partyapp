# Create your views here.
# accounts/views.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    CustomUserLoginForm,
    CustomUserProfileForm,
)
from .models import CustomUser
from .tokens import account_activation_token


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


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    # success_url = reverse_lazy("login")
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
        email.send(fail_silently=settings.EMAIL_FAIL_SILENTLY)


class SignUpConfirmView(TemplateView):
    template_name = "accounts/signup_confirm.html"


class CustomLoginView(LoginView):
    authentication_form = CustomUserLoginForm


class CustomUserListView(LoginRequiredMixin, ListView):
    model = CustomUser
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
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "accounts/update_user.html"
    context_object_name = "objects"
    success_url = reverse_lazy("accounts:users_list")
    permission_required = ["accounts.is_engineer"]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context


class CustomUserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserProfileForm
    template_name = "accounts/user_profile.html"
    context_object_name = "objects"
    success_url = reverse_lazy("landingpage")
