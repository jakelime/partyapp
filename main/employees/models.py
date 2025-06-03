from django.db import models


class EmployeeModel(models.Model):
    name = models.CharField(max_length=256)
    employee_id = models.CharField(max_length=8, unique=True)

    def __str__(self):
        shortened_name = self.name
        if len(self.name) > 13:
            return f"{self.employee_id} ({shortened_name[:10]}...)"
        return f"{self.employee_id} ({self.name})"
