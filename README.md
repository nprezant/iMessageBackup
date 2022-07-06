# iMessageBackup Program

A simple python script to extract iphone message conversations from an iphone backup.

INPUTS:
* iphone backup files
* phone number / email of person you want to extract messages from
  * for group chats (only tested in iOS 15), you must manually determine the chat name

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

#### Group chats

Tested on an iOS 15 backup with a chat from ~2019. The date format for messages seems to have changed at some point so this may fail with very long-running chats.

[This file](https://github.com/richinfante/iphonebackuptools/blob/18c4cc000882afcd71cca71bc32a98391e3aed97/tools/util/apple_timestamp.js) from the `iPhoneBackupTools` project may help if this occurs.

##### Determining chat names

As of current, there is no automated way of determining the chat name. To determine this, go to the backup directory and then:

```
cd 3d
sqlite3 3d0d7e5fb2ce288813306e4d4636395e047a3d28

.headers ON

SELECT
  DATETIME(date / 1000000000 + 978307200, 'unixepoch', 'localtime') as date,
  account,
  text,
  cache_roomnames
FROM message
WHERE cache_roomnames IS NOT NULL
ORDER BY DATE DESC
LIMIT 20;
```

This prints out all group chat messages, most recent first. Use the dates and message contents to try and find the name of the group (`cache_roomnames`).

### File conversions

Browsers cannot currently display HEIC or MOV files.

There is a conversion script available in  `/scripts/file_conversion.sh` which can be run after export is completed.

It requires Linux and uses `ffmpeg` and `libheif` to convert the files and update the URLs in the output HTML files.
