import asyncio
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import eel

from arg import Arguments
from backup import BackupManager

# Initialize tkinter. tkinter is used for folder selection
root = tk.Tk()
root.withdraw()

bm = BackupManager()


@eel.expose
def getLocations():
    """
    :return: current source locations
    """
    return bm.locations


@eel.expose
def addLocation():
    """
    prompts user for source directory and adds it
    """
    location = filedialog.askdirectory()

    # show on successful addition to database
    if bm.add_location(location):
        eel.add_list_item(location)


@eel.expose
def removeLocation(location):
    """
    remove :param location: from source locations
    """
    bm.remove_location(location)


@eel.expose
def askDestination():
    """
    prompts user for backup directory and sets it to destination
    :returns: new destination
    """
    location = filedialog.askdirectory()

    # validation
    p = Path(location)
    if not p.exists() or not p.is_dir() or location == '':
        return bm.destination

    bm.set_destination(location)
    return location


@eel.expose
def setDestination(location):
    """
    sets the :param location: as new destination

    :param location: destination to be set
    :return: whether the operation was successful
    """
    return bm.set_destination(location)


@eel.expose
def setOverwrite(value):
    """
    set :param value: as new overwrite flag
    """
    bm.set_overwrite(value)


@eel.expose
def backup():
    """
    backup current sources to destination
    """

    asyncio.run(bm.backup(True))


@eel.expose
def init():
    """
    ui initiation
    """

    # populate locations
    for location in bm.locations:
        eel.add_list_item(location)

    # set destination
    eel.set_destination(bm.destination)

    # set overwrite
    eel.set_overwrite(bm.overwrite)


if __name__ == '__main__':
    parser = Arguments()
    args = parser.parse_args()

    if args.background:
        asyncio.run(bm.backup(False))
    else:
        eel.init('static')
        eel.start('index.html')
