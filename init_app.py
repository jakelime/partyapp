import os
import subprocess
from typing import Optional

from dotenv import load_dotenv
from main.main.utils import DjangoVersionManager

load_dotenv()
DJANGO_SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
if not DJANGO_SUPERUSER_PASSWORD:
    raise ValueError(
        "DJANGO_SUPERUSER_PASSWORD environment variable is not set. "
        "Please set it in your .env file."
    )


def run_command(cmds: list[str], env: Optional[dict] = None) -> list:
    try:
        print(f"running commands: {' '.join(cmds)}")
        cp = subprocess.run(
            cmds,
            check=True,
            capture_output=True,
            text=True,
        )
        print(cp.stdout)
        if cp.stderr:
            print(cp.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running Django commands: {e.stderr}")
        raise


def run_django_commands():
    try:
        run_command(["python", "main/manage.py", "makemigrations", "accounts"])
        run_command(["python", "main/manage.py", "makemigrations", "employees"])
        run_command(["python", "main/manage.py", "makemigrations", "bingo"])
        run_command(["python", "main/manage.py", "makemigrations", "knowledge"])
        run_command(["python", "main/manage.py", "makemigrations", "obstacle"])
        run_command(["python", "main/manage.py", "migrate"])
        run_command(
            [
                "python",
                "main/manage.py",
                "createsuperuser",
                "--noinput",
                "--username",
                "admin",
                "--email",
                "admin@admin.com",
            ],
            env={
                "DJANGO_SUPERUSER_PASSWORD": DJANGO_SUPERUSER_PASSWORD,
            },
        )
        run_command(["python", "main/manage.py", "import_employees"])
        print("All Django commands executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Django commands: {e}")


def init_version():
    dvm = DjangoVersionManager()
    dvm.write_app_version_file()
    version = dvm.get_app_version()
    print(f"App version initialized: {version}")
    return version


def main():
    init_version()
    run_django_commands()


if __name__ == "__main__":
    main()
