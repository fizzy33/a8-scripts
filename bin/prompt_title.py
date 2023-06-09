#!/usr/bin/env python3


import os
from pathlib import Path
import socket

cwd = Path(os.getcwd()).absolute()


def is_git_root(d) -> bool:
    git_dir = Path(d, ".git")
    return git_dir.exists()


def git_root_name(d) -> str:
    if is_git_root(d):
        return "/ " + d.name + " "
    elif d.parent == d:
        return ""
    else:
        return git_root_name(d.parent)


hostname = socket.gethostname().split(".")[0]

if hostname == "unallocated-static":
    hostname = "stella"

dir_name = git_root_name(cwd)
user = os.getlogin()


print(dir_name + ": " + user + " @ " + hostname)

