from django.db import models
from django.db.models import JSONField, IntegerField, CharField, BooleanField, DateTimeField
import random
import pandas as pd
import logging as lg 
from accounts import models as accounts_models

class winningNumber(models.Model):
    answer = CharField(null=True,blank=True)
    is_valid = BooleanField(default=True)

    submitted_dt = DateTimeField(auto_now = True)

    owner = models.ForeignKey(
        accounts_models.CustomUser,
        on_delete=models.CASCADE,
        null=True,         # Allows the foreign key column to be NULL in the database
        blank=True,        # Allows the field to be blank in forms/admin
        related_name='knowledge_answers' # Access board from employee: employee_instance.bingo_board
    )
