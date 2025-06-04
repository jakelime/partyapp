
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

class ScanItemFindForm(Form):
    ref = CharField(max_length=100, label="Item QR Code")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Field("ref"), Submit("find", "Find"))

    def clean(self):


    def save(self)

    def get(self):

