# main/obstacle/views.py
import logging

from django.views.generic.base import TemplateView

from main.custom_mixin import PasswordlessLoginRequiredMixin

lg = logging.getLogger("django")


class HomeView(PasswordlessLoginRequiredMixin, TemplateView):
    template_name = "home_template.html"
