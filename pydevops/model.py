
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from functools import wraps
import subprocess
import datetime
import os
import shutil
import datetime
from util import logger, runCommand, Path, trace
from abc import ABC, abstractmethod
from datetime import timedelta
import sys
import re


dryRun = True


class Services(ABC):
    @abstractmethod
    def clear_diectory(self, p: Path) -> None:
        pass
    @abstractmethod
    def delete_diectory(self, p: Path) -> None:
        pass
    @abstractmethod
    def gzip_to_archive_dir(self, source: Path, target_dir: Path) -> None:
        pass
 
class DryRunServices(Services):
    @trace
    def clear_diectory(self, p: Path) -> None:
        pass
    @trace
    def delete_diectory(self, p: Path) -> None:
        pass
    @trace
    def gzip_to_archive_dir(self, source: Path, target_dir: Path) -> None:
        pass

class ChangeTheWorldServices(Services):
    @trace
    def clear_diectory(self, p: Path) -> None:
        p.clear_directory()
        
    @trace
    def delete_diectory(self, p: Path) -> None:
        p.delete_tree()

    @trace
    def gzip_to_archive_dir(self, source: Path, target_dir: Path) -> None:
        source.move_and_gzip_to(target_dir)


class CleanerUpper(ABC):
    services: Services
    @abstractmethod
    def run_cleanup(self) -> None:
        pass


@dataclass
class YearMonthDayNestedDirs(CleanerUpper):
    path: Path
    purgeAfter: timedelta

    def run_cleanup(self) -> None:
        for p in self.path.list_entries():
            yearStr = p.basename().strip()
            if len(yearStr) == 4:
                try:
                    year = int(yearStr)
                except:
                    continue
            self.process_month_dirs(year, p)

    def process_month_dirs(self, year: int, year_dir: Path) -> None:
        for m in year_dir.list_entries():
            monthStr = m.basename().strip()
            if len(monthStr) in [1,2]:
                try:
                    month = int(monthStr)
                except:
                    continue
                self.process_day_dirs(year, month, m)


    def process_day_dirs(self, year: int, month: int, month_dir: Path) -> None:
        for d in month_dir.list_entries():
            dayStr = d.basename().strip()
            if len(dayStr) in [1,2]:
                try:
                    day = int(dayStr)
                except:
                    continue
                date = datetime.datetime(year, month, day)
                purgeIfBefore = datetime.datetime.now() - self.purgeAfter
                if date < purgeIfBefore:
                    logger.debug(f"purging {d}")
                    try:
                        self.services.delete_diectory(d)
                    except Exception as e:
                        import traceback
                        logger.error(f"error deleting {d} -- {traceback.format_exc()}")



@dataclass
class YearMonthDayDirs(CleanerUpper):
    path: Path
    purgeAfter: timedelta
    def run_cleanup(self) -> None:
        for p in self.path.list_entries():
            yearMonthDayStr = p.basename().strip()
            date = datetime.datetime.strptime(yearMonthDayStr, "%Y-%m-%d")
            purgeIfBefore = datetime.datetime.now() - self.purgeAfter
            if date < purgeIfBefore:
                logger.debug(f"purging {p}")
                try:
                    self.services.delete_diectory(p)
                except Exception as e:
                    import traceback
                    logger.error(f"error deleting {p} -- {traceback.format_exc()}")


@dataclass
class PostgresLogArchiver(CleanerUpper):
    postgresLogDir: Path
    archivePath: Path
    purgeAfter: timedelta

    def run_cleanup(self) -> None:
        for p in self.postgresLogDir.list_entries():
            if p.is_file():
                self.process_file(p)

    def process_file(self, f: Path) -> None:
        # postgresql-2024-10-15.log
        postgresLogFilePattern = r"postgresql-(\d{4}-\d{2}-\d{2})\.log"
        match = re.match(postgresLogFilePattern, f.basename())
        if match:
            date_str = match.group(1)
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            now = datetime.datetime.now()
            if now.year == date.year and now.month == date.month and now.date == date.date:
                # 
                pass
            else:
                nowDateStr = now.strftime("%Y-%m-%d")
                archiveTo = self.archivePath.join(nowDateStr)
                self.services.gzip_to_archive_dir(f, archiveTo)
        else:
            logger.debug(f"No date found in {f}")

    def purge_old_archive_dirs(self) -> None:
        YearMonthDayDirs(
            path=self.archivePath,
            purgeAfter=self.purgeAfter,
        ).run_cleanup()

@dataclass
class LogArchiver(CleanerUpper):
    sourcePathGlob: str
    archivePath: Path
    purgeAfter: timedelta
    def run_cleanup(self) -> None:
        import glob
        for f in glob.glob(self.sourcePathGlob):
            self.gzip_to_archive_dir(Path(f))

    def gzip_to_archive_dir(self, source: Path) -> None:
        now = datetime.datetime.now()
        nowDateStr = now.strftime("%Y-%m-%d")
        archiveTo = self.archivePath.join(nowDateStr)
        self.services.gzip_to_archive_dir(source, archiveTo)

    def purge_old_archive_dirs(self) -> None:
        YearMonthDayDirs(
            path=self.archivePath,
            purgeAfter=self.purgeAfter,
        ).run_cleanup()


"""


things we need to sort out

    supervisor log files

    journal log max disk space

    cleanup of old postgres log files

    handling warnings and errors in this script


known needs

    clear temp direct

        on all daily process restarts DONE


    expire (YearMonthDayNestedDir | YearMonthDaySingleDir) older than a certage age

        /home/dev/apps/.data/qubes-prod/exports/2024/11/23/
        /home/dev/apps/.cache/runner-prod/exports/2024-11-23/


    gzip files in log archives directories and purge based on age and size

            == ducati-apps ==
        /home/dev/apps/.logs/*/archives/
        /var/log/supervisor/*.log.[0-9]

            == ducati-db ==
        /var/log/pgbackrest/*-[0-9][0-9][0-9].log
        /var/log/postgresql/postgresql-yyyy-mm-dd.log


    daily process restarts

        steps
            get pid from supervisor
            if running / pid is non-zero
                supevisor stop the process 
                confirm the process is stopped
            clear the temp directories
            if it was running
                start the process again


        processes
            syncro-prod
            qubes-prod
            runner-prod
            patientportal-prod

            qubes-beta
            syncro-beta

                
            

"""

@dataclass
class Process:
    name: str
    forceStart: bool

    def __init__(self, name: str, forceStart: bool = False):
        self.name = name
        self.forceStart = forceStart

    # @lazy
    def appdir(self) -> Path:
        return Path(f"/home/dev/apps/{self.name}/")

    def restart(self) -> None:
        process = self
        name = process.name
        logger.debug(f"getting pid for {name}")
        result = runCommand('supervisorctl', 'pid', name, failOnNonZeroReturnCode=False)
        # if result.returncode != 0:
        #     raise Exception(f"Failed to get pid for {name} -- {result.returncode} -- {result.stdout} -- {result.stderr}")

        pid = int(result.stdout.strip())

        running = pid != 0
        if running:
            logger.debug(f"stopping {name}")
            result = runCommand('supervisorctl', 'stop', name)
        else:
            logger.debug(f"{name} is not running")

        appdir = Process(name).appdir()
        tmpdir = appdir.join("tmp")

        logger.debug(f"clearing temp directory {tmpdir}")
        tmpdir.clear_directory()

        appdir.join("cache/client-data-model").clear_directory()

        if running or process.forceStart:
            logger.debug(f"starting {name}")
            result = runCommand('supervisorctl', 'start', name)
        else:
            logger.debug(f"not starting {name} because it was not running")



def loadAppLogsArchiveCleanups() -> list[LogArchiver]:
    entries = []
    home = Path.user_home()
    for p in home.join("apps/.logs/").list_entries():
        archives = p.join("archives")
        if p.exists():
            entries.append(
                LogArchiver(
                    sourcePathGlob = archives.value + "/*",
                    archivePath = Path(f"/backups/logs/{p.basename()}"),
                    purgeAfter = timedelta(days = 5),
                )
            )
    return entries



def run(services: Services, cleanups: list[CleanerUpper], processRestarts: list[Process]) -> None:

    try:
        for cleanup in cleanups:
            try:
                cleanup.services = services
                cleanup.run_cleanup()
            except Exception as e:
                import traceback
                logger.error(f"cleanup failed {cleanup} -- {traceback.format_exc()}")

        for process in processRestarts:
            try:
                logger.debug(f"restarting {process.name}")
                process.restart()
                logger.debug(f"successfully restarted {process.name}")
            except Exception as e:
                import traceback
                logger.error(f"Failed to restart {process.name} -- {traceback.format_exc()}")

        logger.info("completed successfully")

        sys.exit(0)
        
    except Exception as e:
        import traceback
        logger.error(f"Fatal error -- {traceback.format_exc()}")
        sys.exit(1)
