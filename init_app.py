from main.main.utils import DjangoVersionManager

dvm = DjangoVersionManager()
dvm.write_app_version_file()

print(f"{dvm.get_app_version()=}")
