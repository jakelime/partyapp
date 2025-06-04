# main/knowledge/views.py

import logging

from django.views.generic.base import TemplateView

from main.custom_mixin import LoginRequiredMixinNopassword

lg = logging.getLogger("django")


class HomeView(LoginRequiredMixinNopassword, TemplateView):
    template_name = "knowledge/home.html"

class SubmitAnswerView(LoginRequiredMixinNopassword, TemplateView):
    template_name = "knowledge/playerview.html"

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
