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


def get_version():
    return DjangoVersionManager().get_app_version()


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
        # Determine the root directory of the script for relative path calculations
        script_dir = Path(__file__).parent

        match folder_mode.lower():
            case "app_bundles":

                self.version_froot = script_dir / "bundles"
            case "django":
                # This assumes the script is in a 'utils' or similar directory,
                # and manage.py is one level up from that directory's parent.
                # e.g., if script is project_root/app/utils/script.py,
                # then script_dir.parent is project_root/app
                # and script_dir.parent.parent is project_root
                # manage.py would be at project_root/manage.py
                # Original: self.version_froot = Path(__file__).parent
                # This seems to imply app_version.txt is in the same dir as this script for django mode,
                # but then it checks for manage.py in parent.
                # Let's clarify the django path for app_version.txt.
                # If app_version.txt is in django_root/main/main/, and this script is elsewhere,
                # this needs a more robust way to find django_root/main/main/.
                # For now, sticking to original intent for version_froot:
                self.version_froot = script_dir
                # The check for manage.py is relative to version_froot.parent
                # If version_froot is script_dir, then manage.py is expected at script_dir.parent / "manage.py"
                locate_managepy = self.version_froot.parent / "manage.py"
                if not locate_managepy.is_file():
                    # Try another common Django structure: manage.py in the script's parent's parent
                    # e.g. myproject/myapp/utils/version_script.py -> myproject/manage.py
                    locate_managepy_alt = script_dir.parent.parent / "manage.py"
                    if not locate_managepy_alt.is_file():
                        raise RuntimeError(
                            f"VersionManager(folder_mode='{folder_mode}') unable to locate django manage.py "
                            f"at {locate_managepy} or {locate_managepy_alt}"
                        )
                    # If found at alternative, assume app_version.txt path needs to be relative to Django root.
                    # The original code puts app_version.txt in Path(__file__).parent for django mode.
                    # If the intent is django_root/main/main/, this needs adjustment.
                    # For now, keeping self.version_froot as script_dir.
                    # If app_version.txt should be in django_project/main/main/
                    # self.version_froot = locate_managepy.parent / "main" / "main" # Example
            case _:
                self.version_froot = script_dir

        # Ensure the directory for app_version.txt exists
        self.version_froot.mkdir(parents=True, exist_ok=True)

    def write_app_version_file(
        self, version: str = "", filename: str = "app_version.txt"
    ) -> Path:
        fpath = self.version_froot / filename
        with open(fpath, "w") as fwriter:
            fwriter.write(version)
        lg.info(f"app_version={version} updated > {fpath}")
        return fpath

    def get_app_version_from_file(self, filename: str = "app_version.txt") -> str:
        fpath = self.version_froot / filename
        if not fpath.is_file():
            lg.warning(f"Version file not found: {fpath}")
            return "vErr.Err.Err"
        with open(fpath, "r") as fr:
            version = fr.read().strip()
        return version


class CommandManager:
    def __init__(self, env: Optional[dict] = None) -> None:
        self.env = env

    def run(
        self,
        cmd: List[str],
        check: bool = True,
        timeout: Optional[int] = None,
        text: bool = True,  # Changed default to True as per subprocess.run common usage for text mode
        shell: bool = False,
        cwd: Optional[Union[str, Path]] = None,
        show_cmd: bool = False,
    ) -> subprocess.CompletedProcess:
        try:
            if not cmd:
                raise ValueError("no cmd specified")
            if show_cmd:
                lg.info(f"Running command: {' '.join(cmd)} in {cwd or Path.cwd()}")

            # Ensure cwd is a string if it's a Path object for older Python versions if necessary
            # subprocess.run handles Path objects for cwd since Python 3.6+

            results = subprocess.run(
                cmd,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text,  # Process streams as text
                timeout=timeout,
                shell=shell,
                cwd=cwd,
                env=self.env,
            )
            return results
        except subprocess.CalledProcessError as call_error:
            # results object might not be defined if error occurs before subprocess.run call (e.g. timeout in setup)
            # However, CalledProcessError itself contains stdout and stderr if the process ran and exited with error.
            lg.error(
                f"Command '{' '.join(cmd)}' failed with exit code {call_error.returncode}."
            )
            if call_error.stdout:
                lg.error(f"STDOUT:\n{call_error.stdout}")
            if call_error.stderr:
                lg.error(f"STDERR:\n{call_error.stderr}")
            raise call_error
        except FileNotFoundError:
            lg.error(f"Command not found: {cmd[0]}")
            raise
        except Exception as e:
            lg.error(
                f"An unexpected error occurred while running command '{' '.join(cmd)}': {e}"
            )
            raise

    def run_with_output(
        self,
        cmd: List[str],
        check: bool = True,
        timeout: Optional[int] = None,
        text: bool = True,
        shell: bool = False,
        cwd: Optional[Union[str, Path]] = None,
        show_cmd: bool = False,
    ) -> None:

        # Capture results, including potential errors if check=False
        results = self.run(
            cmd,
            check=check,
            timeout=timeout,
            text=text,
            shell=shell,
            cwd=cwd,
            show_cmd=show_cmd,
        )

        # Log stdout/stderr. If text=True, they are already strings.
        if results.stdout:
            lg.info(f"STDOUT:\n{results.stdout}")
        else:
            lg.info("STDOUT: (empty)")

        if results.stderr:
            # stderr might contain warnings even on success, or errors if check=False
            if results.returncode == 0:
                lg.info(f"STDERR (warnings/info):\n{results.stderr}")
            else:
                lg.error(f"STDERR (errors):\n{results.stderr}")
        else:
            lg.info("STDERR: (empty)")


class GitVersionManager:

    error_tag: str = "v0.0.0-git-error"

    def __init__(
        self,
        ver_mgr: VersionManager,
        cmd_mgr: CommandManager,
    ) -> None:
        self.ver_mgr = ver_mgr
        self.cmd_mgr = cmd_mgr
        self.version: Optional[str] = None

    def run_git_get_app_version(self, show_cmd: bool = False) -> str:
        try:
            results = self.cmd_mgr.run(["git", "tag"], show_cmd=show_cmd, text=True)
        except FileNotFoundError:
            lg.error("Git command not found. Is Git installed and in PATH?")
            return "v0.0.0-git-not-found"
        except subprocess.CalledProcessError:
            lg.error("Failed to run 'git tag'. Is this a git repository?")
            return self.error_tag

        tags_output = results.stdout
        if not tags_output:
            lg.warning("No git tags found in 'git tag' output.")
            return self.error_tag

        tags = tags_output.splitlines()

        lg.debug(f"Raw git tags: {tags}")

        # Filter tags that match the "v*.*.*" pattern.
        # This pattern implies at least three numeric components (major.minor.patch).
        # Example: v1.0.0, v0.1.0-alpha
        # It does not strictly enforce that * are numbers, fnmatch is for glob patterns.
        # For more precise filtering (e.g. v<num>.<num>.<num>), a regex could be used.
        filtered_tags = [tag for tag in tags if fnmatch(tag, "v*.*.*")]

        if not filtered_tags:
            lg.warning(f"No tags matched pattern 'v*.*.*' from raw tags: {tags}")
            # Check if any tags exist at all, to provide a more specific warning
            if tags:
                lg.warning(
                    "Consider checking tag naming convention. Expected format like v1.2.3 or v0.1.0-alpha."
                )
            return self.error_tag

        # Sort tags using the natural sort key
        filtered_tags.sort(key=_natural_sort_key)
        lg.debug(f"Sorted filtered tags: {filtered_tags}")

        try:
            latest_tag = filtered_tags[-1]
        except IndexError:
            # This case should be covered by "if not filtered_tags" above,
            # but as a safeguard:
            lg.warning("No git tags found after filtering and sorting.")
            self.error_tag
        return latest_tag

    def get_app_version(self, refresh: bool = False) -> str:
        """
        Gets the app version. If refresh is enabled, it will
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
            return self.version

    def write_app_version_file(
        self,
        version: str = "",
        filename: str = "app_version.txt",
        refresh: bool = False,
    ) -> Path:
        if not version:
            version = self.get_app_version(refresh=refresh)
        # Ensure this method returns the Path object as per its type hint
        return self.ver_mgr.write_app_version_file(version, filename)


class GitCommandManager(CommandManager):
    def __init__(self, env: Optional[dict] = None) -> None:
        super().__init__(env)
        self.version: Optional[str] = None

    def get_app_version(self, refresh: bool = False) -> str:
        if (self.version is not None) and (not refresh):
            return self.version
        else:
            lg.error(
                "GitCommandManager.get_app_version called, but run_git_get_app_version is missing."
            )
            self.version = "v0.0.0-error-gcm-get"
            return self.version

    def write_app_version_file(
        self,
        version: str = "",
        filename: str = "app_version.txt",
        refresh: bool = False,
    ) -> Path:
        if not version:
            version = self.get_app_version(refresh=refresh)
        lg.error(
            "GitCommandManager.write_app_version_file called, "
            "but super().write_app_version_file is invalid."
        )

        raise NotImplementedError(
            "GitCommandManager.write_app_version_file requires a VersionManager."
        )


class DjangoVersionManager(GitVersionManager):
    def __init__(self) -> None:
        # Pass a CommandManager instance to GitVersionManager's constructor
        super().__init__(VersionManager(folder_mode="django"), CommandManager())


class AppVersionManager(GitVersionManager):
    def __init__(self) -> None:
        # Pass a CommandManager instance to GitVersionManager's constructor
        super().__init__(VersionManager(folder_mode="app_bundles"), CommandManager())
