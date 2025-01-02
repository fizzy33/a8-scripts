#!/usr/bin/env python3

import model
from model import ChangeTheWorldServices, PostgresLogArchiver, DryRunServices, Process, CleanerUpper
import util
from util import Path, logger
from datetime import timedelta

import sys

util.requireHostname("ducati-db")


services = DryRunServices()

services = ChangeTheWorldServices()


ducatiDbCleanups: list[CleanerUpper] = [
    PostgresLogArchiver(
        postgresLogDir = Path("/var/log/postgresql/"),
        purgeAfter = timedelta(days = 4),
        archivePath = Path("/backups/logs/postgresql"),
    ),
]


processes: list[Process] = [
]



if __name__=="__main__":
    model.run(
        services=services,
        cleanups=ducatiDbCleanups,
        processRestarts=processes,
    )
    sys.exit(0)

