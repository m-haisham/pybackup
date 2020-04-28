# PyBackup

Backup tool written in python
with **Eel** as GUI

**_NOTE:_** Prompt windows and error windows may appear below the eel window

## Features

- Mutiple folder backup
- file comparison using hash to determine changes

## Console

```text
usage: pybackup.py [-h] [-b]

Backup controller

optional arguments:
  -h, --help        show this help message and exit
  -b, --background  Run the script in background
```

`-b` Runs backup on program start and closes on end. **Eel** window is not opened

## FAQ

### Q. What does overwrite do?

It does different things in two different scenarios.

_Scenario 1:_ old directory of the same name as a file exists. if overwrite is enabled the directory is deleted. otherwise directory is renamed.

_Scenario 2:_ old file of the same name as file with non-matching hash exists. if overwrite is enabled file is deleted. otherwise file is ignored and the current file is not backed up.

### Q. Are all the files copied each backup run?

No. If files of the same name contradictions appear both files are hashed and compared. If the hashes match no further action is taken, Otherwise action is taken according to [overwrite flag](#q-are-all-the-files-copied-each-backup-run).

### Q. How is progress calculated?

Progress is calculated as `currentbytes/totalbytes` transferred.
