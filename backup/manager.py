import math
from pathlib import Path
from typing import List
from shutil import copy2, rmtree
import os

from tkinter import messagebox

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

    async def backup(self, verbose=False):

        def setup(text: str = None, progress: int = None, disable_button: bool = None):
            """
            eel operation setter

            :param text: status text
            :param progress: progress
            :param disable_button: disable backup button
            """

            if not verbose:
                return

            if text is not None:
                eel.set_status_text(text)

            if progress is not None:
                eel.set_progress(progress)

            if disable_button is not None:
                eel.backup_disabled(disable_button)

        def error(title: str, text: str):
            setup(f'{title}. {text}', disable_button=False)
            self.showerror(title, text)

        setup('Validating paths ...', 1, True)

        # copy the variables to avoid them changing partway
        locations = self.locations[:]
        destination = Path(self.destination[:])
        overwrite = bool(self.overwrite)

        # validation
        for location in locations:
            p = Path(location)
            if not p.exists() or not p.is_dir():
                return error('Validation error', location)

        if not destination.exists():

            # check if drive exists
            if not Path(destination.parts[0]).exists():
                return error('Validation error', f'Drive "{destination.parts[0]}" not found.')

            # destination creation prompt
            if self.askyesno('Destination', f'{str(destination)} does not exist. would you like to create it?'):
                destination.mkdir(parents=True, exist_ok=True)

        if not destination.is_dir():
            return error('Validation error', str(destination))

        total = 0
        current = 0

        setup(text='Calculating total size ...')

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
                setup(progress=1 + per)

                # create new path for the backup file
                backedloc = str(path)[len(parentloc):]
                backedpath = Path(str(destination) + backedloc)

                # change status indicator
                setup(text=str(path))

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

                # using shutil.copy2 to preserve metadata
                copy2(str(path), str(backedpath))

        setup('Backup successful.', 100, False)

    def askyesno(self, title, text):
        return messagebox.askyesno(f'PyBackup: {title}', text)

    def showerror(self, title, text):
        return messagebox.showerror(f'PyBackup: {title}', text)

    def save(self):
        self.memory.putall({
            LOCATIONS_KEY: self.locations,
            DESTINATION_KEY: self.destination,
            OVERWRITE_KEY: self.overwrite
        })

        self.memory.save()

    def load(self):
        self.memory.load()

        self.locations = self.memory.get(LOCATIONS_KEY)
        self.destination = self.memory.get(DESTINATION_KEY)
        self.overwrite = self.memory.get(OVERWRITE_KEY)
