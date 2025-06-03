# main/knowledge/views.py

import logging

from django.views.generic.base import TemplateView

from main.custom_mixin import LoginRequiredMixinNopassword

lg = logging.getLogger("django")


class HomeView(LoginRequiredMixinNopassword, TemplateView):
    template_name = "home_template.html"
