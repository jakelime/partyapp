# main/employees/forms.py
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Submit
from django.forms import ModelForm

from . import models


class CssMFieldSmall(Div):
    css_class = "col-md-2"


class CssMFieldSM(Div):
    css_class = "col-md-4"


class CssMFieldMedium(Div):
    css_class = "col-md-6"


class CssMFieldLarge(Div):
    css_class = "col-md-12"


class CssTextBox(Div):
    pass


class EmployeeCreateForm(ModelForm):
    helper = FormHelper()
    helper.form_class = "form-horizontal"
    helper.help_text_inline = True
    layout_elements = [
        Fieldset(
            "Create Employee",
            Div(
                CssMFieldSM("employee_id"),
                CssMFieldLarge("name"),
                css_class="row gx-5",
            ),
            css_class="p-3",
        ),
        Div(
            FormActions(
                Submit(
                    "submit",
                    "Create",
                    css_class="btn btn-primary btn-lg btn-block p-2",
                ),
            ),
            css_class="py-2",
        ),
    ]
    helper.layout = Layout(*layout_elements)

    class Meta:
        model = models.EmployeeModel
        fields = "__all__"
