
from __future__ import annotations

from dataclasses import dataclass, field
import os
import datetime
import subprocess
import shutil


showTraces = True
callDepth = ""
callDepthIndent = "    "


def requireHostname(expectedHostname: str) -> None:
    import socket
    import sys
    actualHostname = socket.gethostname()
    if actualHostname != expectedHostname:
        logger.error(f"expected hostname of ${expectedHostname} does not match actual {actualHostname}")
        sys.exit(1)


@dataclass
class Path:
    value: str

    def __init__(self, value: str, *, _alreadyNormalzied = False):
        if _alreadyNormalzied:
            self.value = value
        else:
            self.value = norm_path(value)

    @staticmethod
    def user_home() -> Path:
        import pathlib
        h = pathlib.Path.home()
        return Path(str(h))

    def make_dirs(self) -> None:
        if not self.exists():
            os.makedirs(self.value)

    def parent(self) -> Path:
        return Path(os.path.dirname(self.value), _alreadyNormalzied=True)

    def basename(self) -> str:
        return os.path.basename(self.value)

    def list_entries(self) -> list[Path]:
        return list_dir(self.value)

    def exists(self) -> bool:
        return os.path.exists(self.value)

    def is_link(self) -> bool:
        return os.path.islink(self.value)

    def is_file(self) -> bool:
        return os.path.isfile(self.value)

    def is_dir(self) -> bool:
        return os.path.isdir(self.value)

    def unlink(self) -> None:
        os.unlink(self.value)

    def delete_tree(self) -> None:
        shutil.rmtree(self.value) 

    def join(self, relpath) -> Path:
        return Path(os.path.join(self.value, relpath))

    def clear_directory(self, mustExist: bool = False) -> None:
        if mustExist or self.exists():
            for p in self.list_entries():
                if p.is_link() or p.is_file():
                    p.unlink()
                elif p.is_dir():
                    p.delete_tree()

    def move_and_gzip_to(self, target_dir: Path) -> None:
        target = target_dir.join(self.basename() + ".gz")
        import gzip
        target_dir.make_dirs()
        with open(self.value, 'rb') as f_in, gzip.open(target.value, 'wb') as f_out:
            f_out.writelines(f_in)
        self.unlink()

def norm_path(p: str) -> str:
    return os.path.normpath(os.path.abspath(p))

def list_dir(dir: str) -> list[Path]:
    absdir = norm_path(dir)
    entires = []
    for f in os.listdir(absdir):
        fp = os.path.join(absdir, f)
        entires.append(Path(fp))
    return entires


def lazy(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Check if result is already computed and cached
        attr_name = f"_{func.__name__}_result"
        if not hasattr(self, attr_name):
            # Compute the result if it hasn't been cached yet
            setattr(self, attr_name, func(self, *args, **kwargs))
        # Return the cached result
        return getattr(self, attr_name)
    return wrapper


def trace(func):
    if not showTraces:
        return func
    def wrapper(*args, **kwargs):
        global callDepth
        zelf = args[0]
        savedCallDepth = callDepth
        callDepth = callDepth + callDepthIndent
        logger.trace(f"{callDepth}Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.trace(f"{callDepth}{func.__name__} returned {result}")
        finally:
            callDepth = savedCallDepth
        return result
    return wrapper


class Logger:
    def trace(self, message: str) -> None:
        self.__logit__("TRACE", message)
    def debug(self, message: str) -> None:
        self.__logit__("DEBUG", message)
    def info(self, message: str) -> None:
        self.__logit__("INFO ", message)
    def warn(self, message: str) -> None:
        self.__logit__("WARN ", message)
    def error(self, message: str) -> None:
        self.__logit__("ERROR", message)
    def __logit__(self, level: str, message: str) -> None:
        ts = str(datetime.datetime.now(datetime.timezone.utc))
        ts = ts.replace(" ", "T")
        ts = ts.replace("+00:00", "Z")
        print(f"{ts} | {level} | {message}")    


logger = Logger()


def runCommand(*args: str, failOnNonZeroReturnCode: bool = True) -> subprocess.CompletedProcess:
        command = " ".join(args)
        logger.debug(f"running command -- {command}")
        result = subprocess.run(args, stdout=subprocess.PIPE)
        if result.returncode != 0 and failOnNonZeroReturnCode:
            raise Exception(f"Failed to run command -- {command} -- {result.returncode} -- {str(result.stdout)} -- {str(result.stderr)}")
        logger.debug(f"running command completed successfully -- {command} -- {result.returncode} -- {str(result.stdout)} -- {str(result.stderr)}")
        return result

