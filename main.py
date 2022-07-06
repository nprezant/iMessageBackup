# -*- coding: utf-8 -*

# works for iOS 10.2 on windows 10

from shutil import copy2, copytree, rmtree
from pathlib import Path

from imessage_backup_tools import MessageBackupReader, DocumentWriter, iMessage

def main():
    '''
    fetch messages and write them to a file
    '''

    # Get inputs

    ## <<<<<<<<<<< MUST BE CHANGED >>>>>>>>>>>>
    iphone_backup_dir = Path('C:/Users/<USERNAME>/AppData/Roaming/Apple Computer/MobileSync/Backup/<GUID>')

    # `me` and `them` only used for HTML output, not for finding the contact
    me = '<MyContactName>'
    them = '<Them>' # other person or name of the group chat

    # Number of messages that are written to at once
    batch_size = 100
    # Number of messages in each HTML document
    document_length = 1000

    out_dir = Path().cwd() / 'export_2'
    out_file = out_dir / 'messages.html'
    if not out_dir.is_dir(): out_dir.mkdir()
    
    attachments_dir = Path().cwd() / 'export_2' / 'attachments'
    if not attachments_dir.is_dir(): attachments_dir.mkdir()

    template_dir = Path().cwd() / 'template'
    template_file = template_dir / 'messages.html'

    # copy template files
    copy2(template_dir / 'messages.css', out_dir / 'messages.css')
    copy2(template_dir / 'messages.js', out_dir / 'messages.js')

    # copy template directories
    img_out_dir = out_dir / 'img'
    if img_out_dir.is_dir(): rmtree(img_out_dir)
    copytree(template_dir / 'img', out_dir / 'img')

    # read messages
    reader = MessageBackupReader(iphone_backup_dir)


    ## <<<<<<<<<<< MUST BE CHANGED >>>>>>>>>>>>
    raw_messages = reader.fetch_by_contact_name(firstname='Mom', lastname=None)
    # raw_messages = reader.fetch_by_contact_info('%111111111%')
    # raw_messages = reader.fetch_groupchat(name='chat123456789012345678')

    # write messages
    writer = DocumentWriter(out_file, template_file)
    writer.write_intro(msg_to=them, msg_from=me)

    num_msgs = len(raw_messages)

    print('creating message objects')
    messages = [iMessage(msg, iphone_backup_dir, attachments_dir, me=me) for msg in raw_messages]
    print(f"{len(messages)} message{'s' if len(messages) != 1 else ''} found")

    html = ''
    for i, msg in enumerate(messages):
        msg.copy_attachment()

        html = html + writer.make_message_html(msg)

        if i != 0 and i % batch_size == 0:
            print(f'making html for message {i}/{num_msgs}')
            writer._append_output(html)
            html = ''

        if i != 0 and i % document_length == 0:
            writer.write_end()

            out_file = out_dir / f"messages {i // document_length}.html"
            writer = DocumentWriter(out_file, template_file)
            writer.write_intro(msg_to=them, msg_from=me)
            print(f"Writing to new file {out_file}")
            html = ''

    writer._append_output(html)
    writer.write_end()

if __name__ == '__main__':
    main()
