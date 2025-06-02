import logging
import re
import secrets
import shutil
import string
import subprocess
import uuid
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from natsort import natsort_keygen

lg = logging.getLogger("django")


def convert_str_to_bool(value):
    mapper = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
    }
    v = value.lower()
    if v in mapper:
        return mapper[v]
    else:
        return False


def get_datetime_str(
    dtformat: str = "%Y%m%d_%H%M%S", append_microseconds: bool = False
) -> str:
    now = datetime.now()
    timestr = now.strftime(dtformat)
    if append_microseconds:
        ms = now.strftime("%f")[:2]
        timestr = f"{timestr}{ms}"
    return timestr


def get_today_date(format):
    today = datetime.today()
    return today.strftime(format)


def get_quarter(dt: datetime):
    month = dt.month
    match month:
        case _ if month in [1, 2, 3]:
            return "Q1"
        case _ if month in [4, 5, 6]:
            return "Q2"
        case _ if month in [7, 8, 9]:
            return "Q3"
        case _ if month in [10, 11, 12]:
            return "Q4"
        case _:
            raise ValueError(f"unable to determine quarter from {dt=}")


def generate_password(length: int = 16) -> str:
    aset = string.ascii_letters + string.digits + string.punctuation
    pwd = "".join(secrets.choice(aset) for _ in range(16))
    return pwd


def generate_unique_id():
    return str(uuid.uuid4())


def is_env_prod(ms_target: Path) -> bool:
    try:
        output_dir = ms_target / create_random_string(6)
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(output_dir)
        return True
    except OSError:
        return False


def create_dev_dir(target_name: str = "media") -> Path:
    output_dir = Path().home() / target_name
    output_dir.mkdir(exist_ok=True)
    return output_dir


def get_static_media_root(ms_root: str = "/media/") -> Path:
    ms_root = Path(ms_root)
    if is_env_prod(ms_root):
        return ms_root
    else:
        return create_dev_dir()


def create_random_string(size: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(size))


def get_job_creation_confidence_level(msg):
    # List of specific word that indicate is a job creation message
    job_related_words = [
        "id",
        "date",
        "day",
        "days",
        "month",
        "start",
        "create",
        "end",
        "tomorrow",
        "id",
        "workscope",
        "task",
        "light",
        "medium",
        "heavy",
        "next",
        "week",
    ]

    # Create a regex pattern that matches any of the specific words
    pattern = r"\b(" + "|".join(job_related_words) + r")\b"

    # Find all matches in the message
    matches = re.findall(pattern, msg.lower(), re.IGNORECASE)

    return len(matches)


def get_version():
    return DjangoVersionManager().get_app_version()


class VersionManager:

    def __init__(self, folder_mode: str = "") -> None:
        """
        Manages version by placing `app_version.txt` within
        source folder.

        Args:
            folder_mode (str, optional): accepts different modes
            [app_bundles, django, *].
            app_bundle mode: places app_version.txt in /app/bundles/
            django mode: places app_version.txt in django_root/main/main/
            * mode: places app_version.txt in Path(__file__).parent
            Defaults to "".

        Raises:
            [Django mode] Raises RuntimeError if unable to locate
            manage.py.
        """
        match folder_mode.lower():
            case "app_bundles":
                self.version_froot = Path(__file__).parent / "bundles"
            case "django":
                self.version_froot = Path(__file__).parent
                locate_managepy = self.version_froot.parent / "manage.py"
                if not locate_managepy.is_file():
                    raise RuntimeError(
                        f"VersionManager({folder_mode=}) unable to locate django manage.py"
                    )
            case _:
                self.version_froot = Path(__file__).parent

    def write_app_version_file(
        self, version: str = "", filename: str = "app_version.txt"
    ) -> Path:
        fpath = self.version_froot / filename
        with open(fpath, "w") as fwriter:
            fwriter.write(version)
        lg.info(f"app_version={version} updated > {fpath}")
        return fpath

    def get_app_version_from_file(self, filename: str = "app_version.txt"):
        fpath = self.version_froot / filename
        with open(fpath, "r") as fr:
            version = fr.read().strip()
        return version


class CommandManager:
    def __init__(self, env: dict | None = None) -> None:
        self.env = env

    def run(
        self,
        cmd: list[str],
        check: bool = True,
        timeout: int | None = None,
        text: str | None = None,
        shell: bool = False,
        cwd: str | Path | None = None,
        show_cmd: bool = False,
    ) -> subprocess.CompletedProcess:
        try:
            if not cmd:
                raise ValueError("no cmd specified")
            if show_cmd:
                lg.info(f"{cmd=}")
            results = subprocess.run(
                cmd,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text,
                timeout=timeout,
                shell=shell,
                cwd=cwd,
                env=self.env,
            )
            return results
        except subprocess.CalledProcessError as call_error:
            try:
                lg.error(f"ERROR:\n{results.stderr}")
            except UnboundLocalError:
                pass
            raise call_error

    def run_with_output(
        self,
        cmd: list[str],
        check: bool = True,
        timeout: int | None = None,
        text: str | None = None,
        shell: bool = False,
        cwd: str | Path | None = None,
        show_cmd: bool = False,
    ) -> None:
        if show_cmd:
            lg.info(f"{cmd=}")
        results = self.run(cmd, check, timeout, text, shell, cwd)
        lg.info(f"stdout:\n{results.stdout.decode()}")
        lg.info(f"stderr:\n{results.stderr.decode()}")


class GitVersionManager:
    def __init__(
        self,
        ver_mgr: VersionManager,
        cmd_mgr: CommandManager,
    ) -> None:
        self.ver_mgr = ver_mgr
        self.cmd_mgr = cmd_mgr
        self.version = None

    def run_git_get_app_version(self, show_cmd: bool = False) -> str:
        results = self.cmd_mgr.run(["git", "tag"], show_cmd=show_cmd)
        tags = results.stdout.decode().splitlines()
        tags = [tag for tag in tags if fnmatch(tag, "v*.*.*")]
        natsort_key = natsort_keygen()
        tags.sort(key=natsort_key)

        try:
            latest_tag = tags[-1]
        except IndexError:
            lg.warning("no git tags found")
            return "v0.0.0"
        return latest_tag

    def run_git_submodule_update(self, cwd: Path) -> None:
        cmds = ["git", "submodule", "update", "--init", "--recursive"]
        lg.info("running git submodule update...")
        self.cmd_mgr.run_with_output(cmd=cmds, cwd=str(cwd.absolute()))

    def get_app_version(self, refresh: bool = False) -> str:
        """gets the app version. if refresh is enabled, it will
        run git tag command to pull the latest tag.

        Args:
            refresh (bool, optional): runs git command to get latest tag. Defaults to False.

        Returns:
            str: version number
        """
        if (self.version is not None) and (not refresh):
            return self.version
        else:
            self.version = self.run_git_get_app_version()
            return self.get_app_version()

    def write_app_version_file(
        self,
        version: str = "",
        filename: str = "app_version.txt",
        refresh: bool = False,
    ) -> Path:
        if not version:
            version = self.get_app_version(refresh=refresh)
        self.ver_mgr.write_app_version_file(version, filename)


class GitCommandManager(CommandManager):
    def __init__(self, env: dict | None = None) -> None:
        super().__init__(env)
        self.version = None

    def get_app_version(self, refresh: bool = False) -> str:
        """gets the app version. if refresh is enabled, it will
        run git tag command to pull the latest tag.

        Args:
            refresh (bool, optional): runs git command to get latest tag. Defaults to False.

        Returns:
            str: version number
        """
        if (self.version is not None) and (not refresh):
            return self.version
        else:
            self.version = self.run_git_get_app_version()
            return self.get_app_version()

    def write_app_version_file(
        self,
        version: str = "",
        filename: str = "app_version.txt",
        refresh: bool = False,
    ) -> Path:
        if not version:
            version = self.get_app_version(refresh=refresh)
        return super().write_app_version_file(version=version, filename=filename)


class DjangoVersionManager(GitVersionManager):
    def __init__(self) -> None:
        super().__init__(VersionManager(folder_mode="django"), CommandManager())


class AppVersionManager(GitVersionManager):
    def __init__(self) -> None:
        super().__init__(VersionManager(folder_mode="bundles"), CommandManager())
