import logging
from pathlib import Path
from typing import Any, Optional, Self

import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as UserGroup
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from employees import models

# cwd from Django defaults to /root/main/manage.py
cwd = Path.cwd().parent
UserModel = get_user_model()

""" Commands for printing to stdout
self.stdout.write(self.style.SUCCESS(f"SUCCESS hello world!{__name__=}")) # bold green
self.stdout.write(self.style.NOTICE(f"NOTICE hello world!{__name__=}")) # reg red
self.stdout.write(self.style.WARNING(f"WARNING hello world!{__name__=}")) # bold yellow
self.stdout.write(self.style.ERROR(f"ERROR hello world!{__name__=}")) # bold red
self.stdout.write(self.style.MIGRATE_HEADING(f"MIGRATE_HEADING hello world!{__name__=}")) # bold blue
self.stdout.write(self.style.MIGRATE_LABEL(f"MIGRATE_LABEL hello world!{__name__=}")) # bold white
self.stdout.write(self.style.SQL_FIELD(f"SQL_FIELD hello world!{__name__=}")) # bold green
self.stdout.write(self.style.SQL_KEYWORD(f"SQL_KEYWORD hello world!{__name__=}")) # regular yellow
"""

EMPLOYEE_ID_COLUMN = "MDM_EMP_ID"
EMPLOYEE_NAME_COLUMN = "NAME"
EMPLOYEE_ID_MAX_LENGTH = 8


class EmployeeDataParser:
    df: Optional[pd.DataFrame] = None

    def __init__(self, path: Path, cmd: BaseCommand) -> Self:
        self.cmd = cmd
        self.path = path
        if not self.path.is_file():
            raise FileNotFoundError(f"Directory {self.path} does not exist.")

    def parse_csv(self):
        df = pd.read_csv(self.path)
        for col_name in [EMPLOYEE_ID_COLUMN, EMPLOYEE_NAME_COLUMN]:
            if col_name not in df.columns:
                raise ValueError(f"Required '{col_name=}' not found in the CSV file.")
        df[EMPLOYEE_ID_COLUMN] = df[EMPLOYEE_ID_COLUMN].apply(
            lambda x: str(x).zfill(EMPLOYEE_ID_MAX_LENGTH)
        )
        df[EMPLOYEE_NAME_COLUMN] = df[EMPLOYEE_NAME_COLUMN].astype(str).str.strip()
        self.df = df

    def load_to_db(self, debug: bool = False) -> None:
        if self.df is None:
            raise ValueError("DataFrame is not initialized. Call parse_csv() first.")
        for _, row in self.df.iterrows():
            emp, created = models.EmployeeModel.objects.get_or_create(
                employee_id=row[EMPLOYEE_ID_COLUMN]
            )
            if created:
                emp.name = row[EMPLOYEE_NAME_COLUMN]
                emp.save()
                self.cmd.stdout.write(
                    self.cmd.style.SUCCESS(f"{emp} saved to database.")
                )
            else:
                if debug:
                    self.cmd.stdout.write(
                        f"{emp} already exists in the database, skipping creation."
                    )


class Command(BaseCommand):
    help = "helper tool to import data from excel file, sync to MLRS database"

    def add_arguments(self, parser):
        parser.add_argument("-p", "--path")
        parser.add_argument("--sync", action="store_true")
        parser.add_argument("-e", "--export", action="store_true")

    def export(self):
        if not getattr(self, "dp", None):
            raise RuntimeError("dataparser is not initialized")
        self.dp.export()

    def sync(self):
        self.stdout.write(self.style.MIGRATE_HEADING("running database sync ..."))
        if not getattr(self, "dp", None):
            raise RuntimeError("dataparser is not initialized")
        # self.dp.db_sync()

    def handle(self, *args, **options):
        path = options["path"]
        if path:
            self.stdout.write(
                self.style.MIGRATE_LABEL(f"custom path specified: {path}")
            )
        else:
            self.stdout.write(
                self.style.MIGRATE_LABEL(
                    "default to reading excel file from `app_local_temp/inputs` dir"
                )
            )
            fpath_dir = settings.APP_LOCAL_TEMP_DIR / "inputs"
            gen = fpath_dir.glob("*.csv")
            fpath = next(gen, None)
            if fpath is None or not fpath.is_file():
                raise CommandError(
                    f"no file found in {fpath_dir}, please place a CSV file of employee data there"
                )
            edp = EmployeeDataParser(fpath, self)
            edp.parse_csv()
            edp.load_to_db()

        if options["export"]:
            self.export()

        if options["sync"]:
            self.sync()
