import subprocess

try:
    from main.utils import DjangoVersionManager
except ImportError:
    from main.main.utils import DjangoVersionManager


def init_version():
    dvm = DjangoVersionManager()
    try:
        version = dvm.get_app_version(run_git_tag=True)
        print(f"App version initialized using git method: {version}")
    except subprocess.CalledProcessError as e:
        version_file_already_exist = dvm.version_file_exists()
        if not version_file_already_exist:
            print(f"ERROR git does not exist on system; {e=}")
        else:
            print(f"{version_file_already_exist=}")
            print(f"{dvm.get_app_version_from_file()=}")


def main():
    init_version()


if __name__ == "__main__":
    main()
