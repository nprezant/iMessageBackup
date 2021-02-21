# iMessageBackup Program

A simple python script to extract iphone message conversations from an iphone backup.

INPUTS:
* iphone backup files
* phone number / email of person you want to extract messages from

OUTPUTS:
* HTML file of all text messages from the specified contact, including image/video attachments (formatted similar to iMessages)
* folder with all attachment images and videos from that conversation

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Python 3 is required. All necessary packages come packaged with python 3.
The paths are set up Windows style, may require a bit of tweaking to work for Mac OS / Unix.

### Script inputs

Set the `BACKUP_PATH` constant to the path to your iphone backup. On Windows 10, it looks something like this:

```python
BACKUP_PATH = 'C:/Users/<USERNAME>/AppData/Roaming/Apple Computer/MobileSync/Backup/<GUID>'
```

Set the `DST_PATH` constant to the path to your destination directory. This is where the output files will be saved. I've just made it the same as my current working directory.

```python
DST_PATH = Path.cwd()
```
