import subprocess

from main.main.utils import DjangoVersionManager


def run_command(cmds: list[str]) -> list:
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


def run_django_commands():
    run_command(["python", "main/manage.py", "makemigrations"])
    run_command(["python", "main/manage.py", "migrate"])
    run_command(["python", "main/manage.py", "import_employees"])
    print("All Django commands executed successfully.")


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
