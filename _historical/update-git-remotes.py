#!/usr/bin/env python3

from pathlib import Path
import os
import subprocess

def process(dir: Path):
  git_dir = dir.joinpath(".git")
  if git_dir.exists():
    try:
      git_url_str = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd = dir).strip().decode("utf-8")
    except:
      print("error processing " + str(dir))
      git_url_str = ""
    if git_url_str.startswith("git@gitlab.com:"):
      import urllib
      url = urllib.parse.urlparse("git://" + git_url_str)
      if url.hostname == "gitlab.com":
        path = url.path[1:].replace("ahs/","customers/")
        new_url = "git@superbee.accur8.zero:" + path
        print(str(dir) + "  " + new_url)
        subprocess.check_output(['git', 'remote', 'set-url', 'origin', new_url], cwd = dir)
  else:
      [process(d) for d in dir.iterdir() if d.is_dir()]



process(Path("."))

