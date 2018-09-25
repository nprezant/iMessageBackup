# iMessageBackup Program

A simple python script to extract iphone message conversations from an iphone backup.

INPUTS:
* iphone backup files
* phone number / email of person you want to extract messages from

OUTPUTS:
* HTML file of all text messages from the specified contact, including attachments (formatted similar to iMessages)
* folder with all attachment images and videos from that conversation

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Python 3 is required. All necessary packages come packaged with python 3.
This code works on Windows 10, but might also work on Mac if you change the file paths.

This repository includes visual studio files, but all that you need for the program to function is the `main.py` script and the `img` directory.

### Installing

Clone the repository

```
git clone https://github.com/nprezant/iMessageBackup.git
```

### Set Up Inputs

Set the `BACKUP_PATH` constant to the path to your iphone backup. Probably looks something like this (replace <USERNAME> with your username):

```python
BACKUP_PATH = 'C:/Users/<USERNAME>/AppData/Roaming/Apple Computer/MobileSync/Backup/3abca6c8b1917981e5c1d8407896df036573f510'
```

Set the `DST_PATH` constant to the path to your destination directory. This is where the output files will be saved. I've just made it the same as my current working directory.

```python
DST_PATH = 'C:/Github/nprezant/iMessageBackup'
```

## Built With

* [Python 3](https://www.python.org/downloads/) - Scripting Language

## Authors

* **Noah Prezant** - *Initial work* - [nprezant](https://github.com/nprezant)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
