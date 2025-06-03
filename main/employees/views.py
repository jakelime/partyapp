from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from .forms import EmployeeCreateForm
from . import models

# Create your views here.


class EmployeeCreateView(CreateView):
    model = models.EmployeeModel
    form_class = EmployeeCreateForm
    template_name = "employees/create.html"
    form_object = None

    def form_valid(self, form):
        record = form.save(commit=False)
        self.form_object = record
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("employees:detail_view", kwargs={"pk": self.form_object.pk})


class EmployeeDetailView(DetailView):
    model = models.EmployeeModel
    template_name = "employees/detail.html"
    context_object_name = "employee"
