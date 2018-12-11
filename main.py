# -*- coding: utf-8 -*

# works for iOS 10.2 on windows 10

import sqlite3
from hashlib import sha1
from shutil import copy2
from pathlib import Path
from string import Template

from imessage_backup_tools import MessageBackupReader, DocumentWriter, iMessage

def main():
    '''
    fetch messages and write them to a file
    '''

    # get inputs
    iphone_backup_folder = Path('C:/Users/Noah/AppData/Roaming/Apple Computer/MobileSync/Backup/3abca6c8b1917981e5c1d8407896df036573f510')
    export_file = Path.cwd() / 'export' / 'message_export.html'
    if not export_file.parent.is_dir(): export_file.parent.mkdir()

    contact_name = dict()
    contact_name['first'] = 'Wren'
    contact_name['last'] = 'Zitney'



    contact_number = '%8282848344%'
    contact_email = '%laurenzitney@gmail.com%'

    header_info = dict()
    header_info['to'] = 'Lauren'
    header_info['from'] = 'Noah'

    template_file = Path('template/messages.html')

    # read messages
    reader = MessageBackupReader(iphone_backup_folder, 'message_query.sql', contact_number, contact_email)
    messages = reader.fetch_all()

    # write messages
    writer = DocumentWriter(export_file, template_file, header_info)

    writer.write_intro()

    total_msg = len(messages)
    i = 0

    for raw_msg in messages:
        i = i + 1
        print(f'writing message {i}/{total_msg}')
        msg = iMessage(raw_msg)
        writer.write_message(msg)

    writer.write_closer()


if __name__ == '__main__':
    main()