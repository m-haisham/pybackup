import math
from pathlib import Path
from typing import List
from shutil import copy2, rmtree
import os

import eel

from .json import JsonMemory

LOCATIONS_KEY = 'LOC'
DESTINATION_KEY = 'DES'
OVERWRITE_KEY = 'OVR'

class BackupManager:
    SAVE_PATH = '.data'

    # locations to be backed up
    locations: List

    # destination for the backups
    destination: str

    # indicates whether to overwrite the files
    overwrite: bool

    def __init__(self, locations=None, destination=None, overwrite=None):
        self.memory = JsonMemory(self.SAVE_PATH)

        self.locations = locations
        if self.locations is None:
            self.locations = self.memory.get(LOCATIONS_KEY, default=[])

        self.destination = destination or self.memory.get(DESTINATION_KEY, default='')

        self.overwrite = overwrite or self.memory.get(OVERWRITE_KEY, default=True)

    def add_location(self, path):
        """
        verifies :param path: to be a valid path and a valid directory
        adds the location to current src locations

        :return: True if added else false
        """

        # validation
        p = Path(path)
        if not p.exists() or not p.is_dir():
            return False

        try:
            self.locations.index(path)
        except ValueError:
            self.locations.append(path)

            self.save()

            # return true to indicate successful operation
            return True
        else:
            # if location already exists, cancel operation
            return False


    def remove_location(self, path):
        """
        removes :param path: from current src locations
        """
        self.locations.remove(path)

        self.save()

    def set_destination(self, path):
        """
        verifies :param path: to be a valid path and a valid directory
        sets :param path: to backup destination

        :return: True if changed else false
        """

        p = Path(path)

        # validation
        p = Path(path)
        if not p.exists() or not p.is_dir():
            return False

        self.destination = path

        self.save()
        return True

    def set_overwrite(self, value):
        self.overwrite = value

        self.save()

    async def backup(self):

        def setup(text: str, progress: int=None, disable_button:bool=None):
            eel.set_status_text(text)

            if progress is not None:
                eel.set_progress(progress)

            if disable_button is not None:
                eel.backup_disabled(disable_button)

        setup('Validating paths ...', 1, True)

        # copy the variables to avoid them changing partway
        locations = self.locations[:]
        destination = Path(self.destination[:])
        overwrite = bool(self.overwrite)

        # validation
        for location in locations:
            p = Path(location)
            if not p.exists() or not p.is_dir():
                return setup(f'Validation error. {location}', disable_button=False)

        if not destination.exists() or not destination.is_dir():
            return setup(f'Validation error. {str(destination)}', disable_button=False)

        total = 0
        current = 0

        # calculate total size
        for location in locations:
            loc = Path(location)
            for path in loc.glob('**/*'):
                if path.is_file():
                    total += path.stat().st_size

        # compare and backup
        for location in locations:
            loc = Path(location)
            parentloc = str(loc.parent)
            for path in loc.glob('**/*'):

                # skip non files.
                if not path.is_file():
                    continue

                # total percentile size transfer
                current += path.stat().st_size
                per = math.floor((current / total) * 100)
                print(per)
                eel.set_progress(1 + per)

                # create new path for the backup file
                backedloc = str(path)[len(parentloc):]
                backedpath = Path(str(destination) + backedloc)

                # change status indicator
                eel.set_status_text(str(path))

                # create directory
                backedpath.parent.mkdir(exist_ok=True, parents=True)

                # check if file exists and whether they are the same file
                if backedpath.exists():

                    if backedpath.is_dir():
                        # if the path is already present as a folder remove/change it
                        if overwrite:
                            rmtree(str(backedpath))
                        else:
                            os.rename(str(backedpath), str(backedpath.parent / Path(f'old_{backedpath.name}')))

                    elif backedpath.is_file():
                        # file is different, delete if flag-overwrite else ignore
                        if hash(path) != hash(backedpath) and overwrite:
                            backedpath.unlink()
                        else:
                            continue

                # using copy2 to preserve metadata
                copy2(str(path), str(backedpath))

        setup('Backup successful.', 100, False)

    def save(self):
        self.memory.put(LOCATIONS_KEY, self.locations)
        self.memory.put(DESTINATION_KEY, self.destination)
        self.memory.put(OVERWRITE_KEY, self.overwrite)

        self.memory.save()

    def load(self):
        self.memory.load()

        self.locations = self.memory.get(LOCATIONS_KEY)
        self.destination = self.memory.get(DESTINATION_KEY)
        self.overwrite = self.memory.get(OVERWRITE_KEY)
