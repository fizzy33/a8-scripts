


import model
from model import Process, YearMonthDayNestedDirs, YearMonthDayDirs, LogArchiver, DryRunServices, ChangeTheWorldServices
import util
from util import Path, logger
from datetime import timedelta
import sys

import socket

util.requireHostname("ducati-apps")

# services = DryRunServices()

services = ChangeTheWorldServices()



ducatiAppsCleanups = [
    YearMonthDayNestedDirs(
        path = Path("/home/dev/apps/.data/qubes-prod/exports/"),
        purgeAfter = timedelta(days = 10),
    ),
    YearMonthDayNestedDirs(
        path = Path("/home/dev/apps/.cache/syncro-prod/tmp/"),
        purgeAfter = timedelta(days = 2),
    ),
    YearMonthDayDirs(
        path = Path("/home/dev/apps/.cache/runner-prod/exports/"),
        purgeAfter = timedelta(days = 2),
    ),
]

ducatiAppsCleanups.extend(model.loadAppLogsArchiveCleanups())





processes = [
    Process("deployedge-beta", forceStart=False),
    Process("esb", forceStart=False),
    Process("ocr-prod", forceStart=False),
    Process("qubes-api", forceStart=False),
    # Process("qubes-beta", forceStart=False),
    # Process("qubes-dev", forceStart=False),
    # Process("qubes-prod", forceStart=True),
    # Process("runner-dev", forceStart=True),
    # Process("runner-prod", forceStart=True),
    Process("syncro-prod", forceStart=False),
]



if __name__=="__main__":
    model.run(
        services=services,
        cleanups=ducatiAppsCleanups,
        processRestarts=processes,
    )

