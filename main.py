# -*- coding: utf-8 -*

# works for iOS 10.2 on windows 10

from shutil import copy2, copytree, rmtree
from pathlib import Path

from imessage_backup_tools import MessageBackupReader, DocumentWriter, iMessage

def main():
    '''
    fetch messages and write them to a file
    '''

    # get inputs
    me = '<MyContactName>'
    iphone_backup_dir = Path('C:/Users/<USERNAME>/AppData/Roaming/Apple Computer/MobileSync/Backup/<GUID>')
    
    out_dir = Path().cwd() / 'export'
    out_file = out_dir / 'messages.html'
    if not out_dir.is_dir(): out_dir.mkdir()
    
    attachments_dir = Path().cwd() / 'export' / 'attachments'
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
    raw_messages = reader.fetch_by_contact_name(firstname='Mom', lastname=None)
    #raw_messages = reader.fetch_by_contact_info('%111111111%')

    # write messages
    writer = DocumentWriter(out_file, template_file)
    writer.write_intro(msg_to='Mom', msg_from=me)

    num_msgs = len(raw_messages)

    print('creating message objects')
    messages = [iMessage(msg, iphone_backup_dir, attachments_dir, me=me) for msg in raw_messages]

    print('writing message html')
    html = ''
    for i, msg in enumerate(messages):
        html = html + writer.make_message_html(msg)
        if i%1000==0:
            print(f'making html for message {i}/{num_msgs}')
            writer._append_output(html)
            html = ''
    writer._append_output(html)

    print('copying attachments')
    for i, msg in enumerate(messages):
        if i%1000==0:
            print(f'copying attachment for message {i}/{num_msgs}')
        msg.copy_attachment()


    writer.write_end()

if __name__ == '__main__':
    main()
