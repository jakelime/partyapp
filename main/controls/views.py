# main/controls/views.py

import logging

from accounts import djfilters as accounts_filters
from accounts import models as accounts_models
from accounts import tables as accounts_tables
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.base import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from main.custom_mixin import CustomLoginRequiredMixin

lg = logging.getLogger("django")


class HomeView(CustomLoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "controls/home.html"
    permission_required = ["accounts.is_gamemaster"]


class UserListView(
    CustomLoginRequiredMixin, PermissionRequiredMixin, SingleTableMixin, FilterView
):
    template_name = "controls/users_list.html"
    permission_required = ["accounts.is_gamemaster"]
    model = accounts_models.CustomUser
    table_class = accounts_tables.UsersListTable
    filterset_class = accounts_filters.CustomUsersFilter
