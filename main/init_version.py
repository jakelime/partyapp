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
    except subprocess.CalledProcessError:
        version = dvm.get_app_version(run_git_tag=False)
        print(f"App version initialized using file-based method: {version}")


def main():
    init_version()


if __name__ == "__main__":
    main()
