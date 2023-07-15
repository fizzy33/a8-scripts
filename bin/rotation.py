
import datetime
from pathlib import Path
import lazyview

class Rotation:

    def __init__(self, serviceName: str, stanzaName: str, rotationName: str, timeDelta: datetime.timedelta):
        self.serviceName = serviceName
        self.stanzaName = stanzaName
        self.rotationName = rotationName
        self.timeDelta = timeDelta
        self.now = datetime.datetime.now()
        self.lastRunFile = Path(f"~/.state/{self.serviceName}-{self.stanzaName}-runs/last-{self.rotationName}").expanduser()
        
        self.loadLastRotation()
        # print(f"lastRotation for {self.name} is {self.lastRun}")
        if self.lastRun is None:
            self.needsRotation = True
            self.nextRotation = None
        else:
            self.nextRotation = self.lastRun + self.timeDelta
            self.needsRotation = self.now >= self.nextRotation

    def loadLastRotation(self) -> datetime.datetime:
        self.lastRun: Optional[datetime.datetime] = None
        if self.lastRunFile.exists():
            # try:
                datetimeStr = self.lastRunFile.read_text()
                self.lastRun = datetime.datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S.%f')
            # except:
                # lastRun = None

    def rotationCompletedSuccessfully(self):
        if self.needsRotation:
            print(f"writing {self.lastRunFile}")
            self.lastRunFile.parent.mkdir(parents=True, exist_ok=True)
            self.lastRunFile.write_text(str(self.now))

def load_rsnapshot_rotations(stanzaName: str) -> lazyview.LazyView:
    return lazyview.from_iter([
        # systemd runs hourly so this will catch it
        Rotation("rsnapshot", stanzaName, "hourly", datetime.timedelta(minutes=50)),
        Rotation("rsnapshot", stanzaName, "daily", datetime.timedelta(days=1)),
        Rotation("rsnapshot", stanzaName, "weekly", datetime.timedelta(days=7)),
        Rotation("rsnapshot", stanzaName, "monthly", datetime.timedelta(days=30)),
        # Rotation("rsnapshot", stanzaName, "yearly", datetime.timedelta(days=365)),
    ])


def load_needed_rsnapshot_rotations(stanzaName: str) -> lazyview.LazyView:
    return load_rsnapshot_rotations(stanzaName).filter(lambda r: r.needsRotation)

