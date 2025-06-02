import datetime
import fnmatch
import logging
import re
import secrets
import shutil
import string
import subprocess
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


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


def get_utc_timestamp_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def get_datetime_str(
    dtformat: str = "%Y%m%d_%H%M%S", append_microseconds: bool = False
) -> str:
    now = datetime.datetime.now()
    timestr = now.strftime(dtformat)
    if append_microseconds:
        ms = now.strftime("%f")[:2]
        timestr = f"{timestr}{ms}"
    return timestr


def get_today_date(format):
    today = datetime.datetime.today()
    return today.strftime(format)


def get_quarter(dt: datetime.datetime):
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


def sanitize_filename(input_string):
    """
    Converts any user input string into an alphanumeric name suitable for
    use as a filename in Windows or Linux operating systems.

    Args:
      input_string: The string to be converted.

    Returns:
      A new string containing only alphanumeric characters.
    """
    # Remove any characters that are not alphanumeric
    sanitized_string = re.sub(r"[^a-zA-Z0-9]", "", input_string)
    return sanitized_string


def natural_sort(mylist):
    """
    Sorts a list of strings in natural order, handling version numbers.

    Args:
        mylist: The list of strings to sort.

    Returns:
        A new list with the strings sorted in natural order.
    """

    def convert(text):
        return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", text)]

    return sorted(mylist, key=convert)


class VersionManager:
    version_froot: Path | None = None
    version_file: Path | None = None
    filename: str = "app_version.txt"

    def __init__(self, app_version_mode: str = "app_bundles") -> None:
        match app_version_mode.casefold():
            case "app_bundles":
                self.init_mode_app_bundles()
            case "django":
                self.init_mode_django()
            case _:
                raise NotImplementedError(f"{app_version_mode=}")
        self.version_file = self.version_froot / self.filename

    def init_mode_app_bundles(self) -> None:
        self.version_froot = Path(__file__).parent / "bundles"
        self.version_froot.mkdir(parents=True, exist_ok=True)

    def init_mode_django(self) -> None:
        self.version_froot = Path(__file__).parent
        locate_managepy = self.version_froot.parent / "manage.py"
        if not locate_managepy.is_file():
            raise RuntimeError("init_mode_django unable to locate django manage.py")

    def write_app_version_file(
        self, version: str = "", fpath: Optional[Path] = None
    ) -> Path:
        if fpath is None:
            fpath = self.version_file
        with open(fpath, "w") as fwriter:
            fwriter.write(version)
        lg.info(f"app_version={version} updated > {fpath}")
        return fpath

    def get_app_version_from_file(self, fpath: Optional[Path] = None) -> str:
        if fpath is None:
            fpath = self.version_file
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


class GitVersionTemplate(ABC):
    vm: VersionManager = None
    cm: CommandManager = None

    @abstractmethod
    def init_versionmanager(self, app_version_mode: str):
        # return VersionManager(app_version_mode)
        pass

    @abstractmethod
    def init_commandmanager(self, env: Optional[dict]):
        # return VersionManager(app_version_mode)
        pass

    def runcmd_get_git_tag_version(self, show_cmd: bool = False) -> str:
        try:
            results = self.cm.run(["git", "tag"], show_cmd=show_cmd)
        except Exception as e:
            return "frozenGitVersion"
        tags = results.stdout.decode().splitlines()
        tags = [tag for tag in tags if fnmatch.fnmatch(tag, "v*.*.*")]
        tags = natural_sort(tags)

        try:
            latest_tag = tags[-1]
        except IndexError:
            lg.warning("no git tags found")
            return "v0.0.0"
        return latest_tag

    def get_version(self, skip_git_cmd: bool = False, refresh=False) -> str:
        ver = ""
        if refresh and not skip_git_cmd:
            self.run_git_tag_and_write_to_file()

        ver = self.vm.get_app_version_from_file()

        if not ver:
            if skip_git_cmd:
                return "verError"
            else:
                ver = self.runcmd_get_git_tag_version()
                self.vm.write_app_version_file(ver)
                return self.get_version(skip_git_cmd=True)

        return ver

    def run_git_tag_and_write_to_file(self) -> Path | None:
        ver = self.runcmd_get_git_tag_version()
        if ver:
            path = self.vm.write_app_version_file(ver)
            return path
        return None


class GitVersionManager(GitVersionTemplate):
    def __init__(self, app_version_mode: str = "app_bundles", env: dict | None = None):
        self.vm = self.init_versionmanager(app_version_mode)
        self.cm = self.init_commandmanager(env)

    def init_versionmanager(self, app_version_mode):
        return VersionManager(app_version_mode)

    def init_commandmanager(self, env):
        return CommandManager(env)


class DjangoVersionManager(GitVersionTemplate):
    def __init__(self, env: dict | None = None):
        self.vm = self.init_versionmanager()
        self.cm = self.init_commandmanager(env)

    def init_versionmanager(self):
        return VersionManager("django")

    def init_commandmanager(self, env):
        return CommandManager(env)
