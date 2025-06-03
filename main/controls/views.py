# main/controls/views.py

import logging
import threading
from collections import namedtuple

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from accounts import djfilters as accounts_filters
from accounts import models as accounts_models
from accounts import tables as accounts_tables

lg = logging.getLogger("django")


class HomeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "controls/home.html"
    permission_required = ["accounts.is_gamemaster"]


class UserListView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    template_name = "controls/users_list.html"
    permission_required = ["accounts.is_gamemaster"]
    model = accounts_models.CustomUser
    table_class = accounts_tables.UsersListTable
    filterset_class = accounts_filters.CustomUsersFilter
