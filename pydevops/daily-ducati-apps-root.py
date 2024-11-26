


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
    LogArchiver(
        sourcePathGlob = "/var/log/supervisor/*.log.[0-9]",
        archivePath = Path("/backups/logs/supervisor"),
        purgeAfter = timedelta(days = 5),
    )
]


processes = [
]


if __name__=="__main__":
    model.run(
        services=services,
        cleanups=ducatiAppsCleanups,
        processRestarts=processes,
    )

