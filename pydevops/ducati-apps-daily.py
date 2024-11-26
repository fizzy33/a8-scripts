


import model
from model import Process, YearMonthDayNestedDirs, YearMonthDayDirs, LogArchiver, DryRunServices, ChangeTheWorldServices
import util
from util import Path, logger
from datetime import timedelta
import sys

import socket

util.requireHostname("ducati-apps")

services = DryRunServices()




ducatiAppsCleanups = [
    YearMonthDayNestedDirs(
        path = Path("/home/dev/apps/.data/qubes-prod/exports/"),
        purgeAfter = timedelta(days = 10),
    ),
    YearMonthDayDirs(
        path = Path("/home/dev/apps/.cache/runner-prod/exports/"),
        purgeAfter = timedelta(days = 2),
    ),
    LogArchiver(
        sourcePathGlob = "/var/log/supervisor/*.log.[0-9]",
        archivePath = Path("/backups/logs/supervisor"),
        purgeAfter = timedelta(days = 5),
    )
]

ducatiAppsCleanups.extend(model.loadAppLogsArchiveCleanups())





processes = [
    Process("deployedge-beta", forceStart=False),
    # Process("esb", forceStart=True),
    # Process("ocr-prod", forceStart=True),
    # Process("qubes-api", forceStart=True),
    Process("qubes-beta", forceStart=False),
    Process("qubes-dev", forceStart=False),
    # Process("qubes-prod", forceStart=True),
    Process("runner-dev", forceStart=True),
    # Process("runner-prod", forceStart=True),
    # Process("syncro-prod", forceStart=True),
]


def main():

    for cleanerUpper in ducatiAppsCleanups:
        try:
            logger.debug(f"running cleanup {cleanerUpper}")
            cleanerUpper.services = services
            cleanerUpper.run_cleanup()
        except Exception as e:
            import traceback
            logger.error(f"cleanup failed {cleanerUpper} -- {traceback.format_exc(e)}")
        
    for process in processes:
        try:
            logger.debug(f"restarting {process.name}")
            process.restart()
            logger.debug(f"successfully restarted {process.name}")
        except Exception as e:
            import traceback
            logger.error(f"Failed to restart {process.name} -- {traceback.format_exc(e)}")



if __name__=="__main__":
    model.run(
        services=services,
        cleanups=ducatiAppsCleanups,
        processRestarts=processes,
    )

