try:
    from main.utils import DjangoVersionManager
except ImportError:
    from main.main.utils import DjangoVersionManager


def init_version():
    dvm = DjangoVersionManager()
    dvm.write_app_version_file()
    version = dvm.get_app_version()
    print(f"App version initialized: {version}")
    return version


def main():
    init_version()


if __name__ == "__main__":
    main()
