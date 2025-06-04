import logging
import random
import re
import secrets
import shutil
import string
import subprocess
import uuid
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

CHARACTERS = string.ascii_lowercase + string.digits
WORD_LIST = [
    "apple",
    "banana",
    "cherry",
    "date",
    "elderberry",
    "fig",
    "grape",
    "kiwi",
    "lemon",
    "mango",
    "nectarine",
    "orange",
    "papaya",
    "quince",
    "raspberry",
    "strawberry",
    "tangerine",
    "ugli",
    "vanilla",
    "watermelon",
    "xigua",
    "yuzu",
    "zucchini",
    "art",
    "ball",
    "cat",
    "dog",
    "eat",
    "fly",
    "go",
    "help",
    "ink",
    "jump",
    "kite",
    "love",
    "moon",
    "nest",
    "open",
    "play",
    "quiet",
    "run",
    "sing",
    "talk",
    "use",
    "view",
    "walk",
    "yell",
    "zip",
    "blue",
    "green",
    "red",
    "yellow",
    "fast",
    "slow",
    "big",
    "small",
    "happy",
    "sad",
    "bright",
    "dark",
    "cloud",
    "sun",
    "star",
    "tree",
    "flower",
    "ocean",
    "river",
    "mountain",
    "valley",
]


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


def generate_random_email(name: Optional[str] = None) -> str:
    if not name:
        name = f"{random.choice(WORD_LIST)}-{''.join(random.choices(CHARACTERS, k=6))}"
    domain_suffixes = [".com", ".net", ".org", ".edu", ".gov"]
    domain_name = random.choice(WORD_LIST)
    domain_suffix = random.choice(domain_suffixes)
    return f"{name}@{domain_name}{domain_suffix}"


def _natural_sort_key(version_string: str) -> Tuple[Union[str, int], ...]:
    """
    Creates a sort key for natural string sorting (human sorting).
    E.g., "v1.2.10" should come after "v1.2.9".
    Handles components like "v1.2.10-alpha".
    Splits the string into alternating sequences of non-digits and digits.
    """
    if not isinstance(version_string, str):
        # Handle non-string inputs if necessary, or rely on type checking.
        # For simplicity, assuming string input as per typical version tags.
        return (version_string,)

    # Find all sequences of digits (\d+) or sequences of non-digits (\D+)
    components = re.findall(r"(\d+)|(\D+)", version_string)

    key_parts: List[Union[str, int]] = []
    for digit_part, non_digit_part in components:
        if digit_part:  # If it's a number string
            key_parts.append(int(digit_part))
        elif non_digit_part:  # If it's a non-number string
            key_parts.append(non_digit_part)

    return tuple(key_parts)


class CommandManager:
    def run(
        self,
        cmd: List[str],
        check: bool = True,
        timeout: Optional[int] = None,
        text: bool = True,
        shell: bool = False,
        cwd: Optional[Union[str, Path]] = None,
        show_cmd: bool = False,
        env: Optional[dict] = None,
    ) -> subprocess.CompletedProcess:
        # This method uses print statements, not logger because
        # the Django app logger may not have been initialized yet.
        try:
            if not cmd:
                raise ValueError("no cmd specified")
            if show_cmd:
                lg.info(f"Running command: {' '.join(cmd)} in {cwd or Path.cwd()}")

            results = subprocess.run(
                cmd,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text,  # Process streams as text
                timeout=timeout,
                shell=shell,
                cwd=cwd,
                env=env,
            )
            return results

        except subprocess.CalledProcessError as call_error:
            print(
                f"Command '{' '.join(cmd)}' failed with exit code {call_error.returncode}."
            )
            if call_error.stdout:
                print(f"STDOUT:\n{call_error.stdout}")
            if call_error.stderr:
                print(f"STDERR:\n{call_error.stderr}")
            raise call_error

        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")
            raise

        except Exception as e:
            print(
                f"An unexpected error occurred while running command '{' '.join(cmd)}': {e}"
            )
            raise


class GitCommandManager(CommandManager):
    error_tag: str = "v0.0.0-error"

    def run_git_tag(self, debug_mode: bool = False) -> str:
        # This method uses print statements, not logger because
        # the Django app logger may not have been initialized yet.
        try:
            results = self.run(["git", "tag"], text=True)
        except Exception:
            raise

        tags_output = results.stdout
        if not tags_output:
            print("No git tags found in 'git tag' output.")
            return self.error_tag
        tags = tags_output.splitlines()
        if debug_mode:
            print(f"Raw git tags: {tags}")
        filtered_tags = [tag for tag in tags if fnmatch(tag, "v*.*.*")]
        if not filtered_tags:
            print(f"No tags matched pattern 'v*.*.*' from raw tags: {tags}")
            # Check if any tags exist at all, to provide a more specific warning
            if tags:
                print(
                    "Consider checking tag naming convention. Expected format like v1.2.3 or v0.1.0-alpha."
                )
            return self.error_tag
        filtered_tags.sort(key=_natural_sort_key)
        if debug_mode:
            print(f"Sorted filtered tags: {filtered_tags}")
        try:
            latest_tag = filtered_tags[-1]
        except IndexError:
            # This case should be covered by "if not filtered_tags" above,
            # but as a safeguard:
            print("No git tags found after filtering and sorting.")
            self.error_tag
        return latest_tag


class VersionManager:
    cmd_manager: CommandManager
    version_fpath_root: Optional[Path] = None
    app_ver_filename: str = "app_version.txt"
    app_ver_filepath: Optional[Path] = None
    version: str = "v0.0.0-error"

    def __init__(
        self,
        folder_mode: str = "app_bundles",
        app_ver_filename: str = "app_version.txt",
    ) -> None:
        self.gcm = GitCommandManager()
        self.version_fpath_root = self.init_root_folder_for_appversion_file(folder_mode)
        self.app_ver_filename = app_ver_filename
        self.app_ver_filepath = self.version_fpath_root / self.app_ver_filename

    def init_root_folder_for_appversion_file(self, folder_mode: str = "") -> Path:
        """Initializes the root folder for the app version file based on the specified mode."""
        # Determine the root directory of the script for relative path calculations
        script_dir = Path(__file__).parent

        match folder_mode.lower():
            case "app_bundles":
                f_root = script_dir / "bundles"
            case "django":
                f_root = script_dir
                locate_managepy = f_root.parent / "manage.py"
                if not locate_managepy.is_file():
                    # Try another common Django structure: manage.py in the script's parent's parent
                    # e.g. myproject/myapp/utils/version_script.py -> myproject/manage.py
                    locate_managepy_alt = script_dir.parent.parent / "manage.py"
                    if not locate_managepy_alt.is_file():
                        raise RuntimeError(
                            f"VersionManager(folder_mode='{folder_mode}') unable to locate django manage.py "
                            f"at {locate_managepy} or {locate_managepy_alt}"
                        )
            case _:
                f_root = script_dir

        f_root.mkdir(parents=True, exist_ok=True)
        return f_root

    def write_app_version_file(self, version: str = "") -> Path:
        # This method uses print statements, not logger because
        # the Django app logger may not have been initialized yet.
        with open(self.app_ver_filepath, "w") as fwriter:
            fwriter.write(version)
        print(f"app_version={version} updated > {self.app_ver_filepath}")
        return self.app_ver_filepath

    def get_app_version_from_file(self) -> str:
        if not self.app_ver_filepath.is_file():
            print(f"Version file not found: {self.app_ver_filepath}")
            return self.version
        with open(self.app_ver_filepath, "r") as fr:
            version = fr.read().strip()
            print(f"{version=}")
        self.version = version
        return self.version

    def get_app_version(self, run_git_tag: bool = False) -> str:
        """Retrieves the application version either from a git tag or from a file."""
        if run_git_tag:
            try:
                version = self.update_app_version_from_git()
                return version
            except subprocess.CalledProcessError:
                raise
        else:
            return self.get_app_version_from_file()

    def update_app_version_from_git(self) -> str:
        """Runs `git tag` command to get the latest version tag,
        then writes it to the app version file."""
        self.version = self.gcm.run_git_tag()
        self.write_app_version_file(self.version)
        return self.version

    def version_file_exists(self) -> bool:
        """Checks if the app version file exists."""
        return self.app_ver_filepath.is_file()


class GenericAppVersionManager(VersionManager):
    def __init__(self, folder_mode="app_bundles", app_ver_filename="app_version.txt"):
        super().__init__(folder_mode, app_ver_filename)


class DjangoVersionManager(VersionManager):
    def __init__(self, folder_mode="django", app_ver_filename="app_version.txt"):
        super().__init__(folder_mode, app_ver_filename)
