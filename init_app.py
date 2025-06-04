import os
import subprocess
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
try:
    from main.init_version import init_version
except ImportError:
    from init_version import init_version 

load_dotenv()
DJANGO_SUPERUSER_PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
if not DJANGO_SUPERUSER_PASSWORD:
    raise ValueError(
        "DJANGO_SUPERUSER_PASSWORD environment variable is not set. "
        "Please set it in your .env file."
    )


def locate_manage_py(manage_py_filename:str = "manage.py") -> str:
    """
    Locate the manage.py file in the main directory.
    """
    pathname_relative_to_cwd = "manage.py"
    cwd = Path(__file__).parent
    manage_py = cwd / manage_py_filename
    if manage_py.is_file():
        return pathname_relative_to_cwd
    else:
        manage_py = cwd / "main" / manage_py_filename
        if manage_py.is_file():
            pathname_relative_to_cwd = "main/manage.py"
            return pathname_relative_to_cwd
    raise FileNotFoundError(f"unable to locate manage.py in {cwd=} or `cwd`/main")
    
    
def run_command(
    cmds: list[str], env: Optional[dict] = None, check: bool = True
) -> list:
    try:
        print(f"running commands: {' '.join(cmds)}")
        cp = subprocess.run(
            cmds,
            check=check,
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
    manage_py = locate_manage_py()
    try:
        run_command(["python", manage_py, "makemigrations", "accounts"])
        run_command(["python", manage_py, "makemigrations", "employees"])
        run_command(["python", manage_py, "makemigrations", "bingo"])
        run_command(["python", manage_py, "makemigrations", "knowledge"])
        run_command(["python", manage_py, "makemigrations", "obstacle"])
        run_command(["python", manage_py, "migrate"])
        run_command(
            [
                "python",
                manage_py,
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
            check=False,
        )
        run_command(["python", manage_py, "import_employees"])
        run_command(["python", manage_py, "collectstatic", "--noinput"])
        print("All Django commands executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR!!! While running Django commands:\n{e}")


def main():
    init_version()
    run_django_commands()


if __name__ == "__main__":
    main()
