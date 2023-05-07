#!/usr/bin/python

import sys

"""
This script will do a dump restore to the TARGET_DB.  Note the TARGET_DB will get cleared.
"""

REMOTE_SSH=sys.argv[1]
REMOTE_DB=sys.argv[2]
TARGET_DB=sys.argv[3]


def run_shell_command(command, fail_on_error=True):
  from subprocess import check_call
  print "running -- " + command
  try:
    check_call(command, shell=True)
  except Exception as e:
    if fail_on_error:
      raise e


run_shell_command("dropdb " + TARGET_DB, False)
run_shell_command("createdb " + TARGET_DB)


dump_restore_cmd = "ssh " + REMOTE_SSH + ' "sudo -u postgres pg_dump --no-privileges --no-owner ' + REMOTE_DB + ' | gzip" | gunzip | psql ' + TARGET_DB

run_shell_command(dump_restore_cmd)


