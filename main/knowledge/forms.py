
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Field, Layout, Row, Submit
from django.core.exceptions import ValidationError
from django.forms import (
    CharField,
    ChoiceField,
    FloatField,
    Form,
    IntegerField,
    Textarea,
    DateField,
    BooleanField,
    TextInput,
    FileField,
)
from .models import KnowledgeAnswer
from django.core.validators import FileExtensionValidator


