from datetime import timedelta

import django_filters
from django.utils import timezone
from django_filters import BooleanFilter, FilterSet

from . import models as accounts_models


class CustomUsersFilter(FilterSet):
    has_claimed = BooleanFilter()

    class Meta:
        model = accounts_models.CustomUser
        fields = {
            "username": ["icontains"],
            "preferred_name": ["icontains"],
        }
