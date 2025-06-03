import django_tables2 as djt
from django.core.paginator import Paginator

from . import models as accounts_models


class UsersListTable(djt.Table):

    class Meta:
        model = accounts_models.CustomUser
        # template_name = "django_tables2/bootstrap.html"
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = (
            "id",
            "username",
            "preferred_name",
            "has_claimed",
        )

    def paginate(
        self, paginator_class=Paginator, per_page=50, page=1, *args, **kwargs
    ):
        """
        Paginates the table using a paginator and creates a ``page`` property
        containing information for the current page.

        Arguments:
            paginator_class (`~django.core.paginator.Paginator`): A paginator class to
                paginate the results.

            per_page (int): Number of records to display on each page.
            page (int): Page to display.

        Extra arguments are passed to the paginator.

        Pagination exceptions (`~django.core.paginator.EmptyPage` and
        `~django.core.paginator.PageNotAnInteger`) may be raised from this
        method and should be handled by the caller.
        """

        per_page = per_page or self._meta.per_page
        self.paginator = paginator_class(self.rows, per_page, *args, **kwargs)
        self.page = self.paginator.page(page)

        return self
