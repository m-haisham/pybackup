import asyncio

import eel
import tkinter as tk
from tkinter import filedialog
from backup import BackupManager

from pathlib import Path

# Initialize tkinter. tkinter is used for folder selection
root = tk.Tk()
root.withdraw()

bm = BackupManager()

@eel.expose
def getLocations():
    return bm.locations

@eel.expose
def addLocation():
    location = filedialog.askdirectory()

    # show on successful addition to database
    if bm.add_location(location):
        eel.add_list_item(location)

@eel.expose
def removeLocation(location):
    bm.remove_location(location)

@eel.expose
def askDestination():
    location = filedialog.askdirectory()

    # validation
    p = Path(location)
    if not p.exists() or not p.is_dir() or location == '':
        return bm.destination

    bm.set_destination(location)
    return location

@eel.expose
def setDestination(location):
    return bm.set_destination(location)

@eel.expose
def setOverwrite(value):
    bm.set_overwrite(value)

@eel.expose
def backup():
    asyncio.run(bm.backup())

@eel.expose
def init():
    # populate locations
    for location in bm.locations:
        eel.add_list_item(location)

    # set destination
    eel.set_destination(bm.destination)

    # set overwrite
    eel.set_overwrite(bm.overwrite)

# HELPER FUNCTION
@eel.expose
def eprint(v):
    print(v)

eel.init('static')
eel.start('index.html')

if __name__ == '__main__':
    pass
