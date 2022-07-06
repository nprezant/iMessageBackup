
import sqlite3
from hashlib import sha1
from shutil import copy2
from pathlib import Path
from string import Template


def format_date(date, sep='.'):
    '''
    takes a date formatted YYYYMMDD and returns
    a date formatted MM.DD.YYYY
    '''
    return date[4:6] + sep + date[6:8] + sep + date[0:4]


class iMessage:
    def __init__(self, msg, backup_dir, media_output_dir, me='me'):
        self.raw_message = msg
        self.backup_dir = backup_dir
        self.media_output_dir = media_output_dir

        self.uniqueID = msg[1]
        self.time = msg[3]
        self.date = format_date(msg[4])
        
        if msg[2] == 1:
            self.is_from_me = True
            self.firstname = me
            self.lastname = None
        else:
            self.is_from_me = False
            if len(msg) > 8 and msg[8] is not None:
                self.firstname = msg[8]
            else:
                self.firstname = self.uniqueID

            if len(msg) > 9 and msg[9] is not None:
                self.lastname = msg[9]
            else:
                self.lastname = None

        if (msg[7] is not None) and (not msg[7] == ''):
            self.has_attachment = True
            self.attachment_src_path = self.backup_dir / self._get_attachment_source(msg[7])
            self.attachment_filename = self.media_output_dir / self._get_attachment_filename(msg[7])
        else:
            self.has_attachment = False
            
        if msg[6] is not None:
            self.has_text = True
            self.text = msg[6]
        else:
            self.has_text = False


    def copy_attachment(self):
        '''
        copies the message attachment to the destination directory
        :backup_dir: path to the iphone backup folder
        Will change `output_path` if the file already exists in the destination directory
        '''
        if self.has_attachment:
            try:
                output_path = Path(self.attachment_filename)
                original_path = output_path
                count = 0
                while output_path.exists():
                    filename = original_path.parts[-1].split(".")
                    new_filename = ".".join(filename[:-1]) + " (" + str(count) + ")." + filename[-1]
                    output_path = original_path.with_name(new_filename)
                    count += 1

                if count != 0:
                    print(f"attachment {self.attachment_filename} renamed to {output_path.resolve()}")
                    self.attachment_filename = output_path.resolve()
                copy2(self.attachment_src_path, self.attachment_filename)
                return 
            except FileNotFoundError:
                print(f'attachment file not found: {self.attachment_src_path}')


    def _get_attachment_filename(self, raw_path):
        '''
        gets the filename of an attachment
        '''
        return raw_path.split('/')[-1] # gets the file name, e.g. IMG_2613.PNG


    def _get_attachment_source(self, raw_path):
        '''
        finds the source path to the attachment file
        relative to the iphone backup directory
        '''
        ext = raw_path.split('.')[-1] # gets the file extension, e.g. PNG
        if (ext.lower() in ['jpg', 'png', 'mov', 'jpeg', 'gif']) or True:
            domainpath = 'MediaDomain-' + raw_path[2:] # create the domain path that will be hashed
            filename = sha1(domainpath.encode('utf-8')).hexdigest() # create the SHA1 hash (which is the file name)
            dir = filename[:2] # the first two digets of the filename are the directory name
            return Path(dir, filename) # create an file path to the attachment
        else:
            print(f'skipped over {ext} type file')
            #raise ValueError('FILE NAME I DON\'T KNOW HOW TO DEAL WITH WHAT DO I DO')
        

class MessageBackupReader:
    def __init__(self, iphone_backup_dir):
        self._message_db_file = str(iphone_backup_dir / '3d' / '3d0d7e5fb2ce288813306e4d4636395e047a3d28')
        self._contacts_db_file = str(iphone_backup_dir / '31' / '31bb7ba8914766d4ba40d6dfb6113c8b614be442')


    def fetch_by_contact_name(self, firstname, lastname, get_all:bool=False):
        '''
        fetches all the messages using just the first and last name of the contact
        '''
        query_exe_inputs = dict()

        if firstname is None:
            firstname_query = 'AND FirstName is null'
        else:
            firstname_query = 'AND FirstName LIKE :firstname'
            query_exe_inputs['firstname']=firstname

        if lastname is None:
            lastname_query = 'AND LastName is null'
        else:
            lastname_query = 'AND LastName LIKE :lastname'
            query_exe_inputs['lastname']=lastname

        whereclause = firstname_query + ' ' + lastname_query

        if get_all:
            whereclause = ''
            query_exe_inputs = dict()

        conn = sqlite3.connect(self._message_db_file)
        conn.execute(f'ATTACH DATABASE [{self._contacts_db_file}] AS contacts')

        query = self._read('select_msg_from_name.sql')
        query = Template(query).safe_substitute(dict(whereclause=whereclause))

        cursor = conn.cursor()
        cursor.execute(query, query_exe_inputs)
        messages = cursor.fetchall()
        return messages

    
    def fetch_by_contact_info(self, *args):
        '''
        contact_number = '%8282832222%, contact_email='someone@example.com'
        fetches all messages from the iphone backup directory
        using the supplied query file
        :return: iterable of all messages
        '''
        query_exe_inputs = tuple(args)

        whereclause = ""
        for i in range(len(query_exe_inputs)):
            if i == 0:
                whereclause = 'AND UniqueID like ?'
            else:
                whereclause = whereclause + ' OR UniqueID like ?'

        query = self._read('select_msg_from_name.sql')
        query = Template(query).safe_substitute(dict(whereclause=whereclause))

        conn = sqlite3.connect(self._message_db_file)
        conn.execute(f'ATTACH DATABASE [{self._contacts_db_file}] AS contacts')

        cursor = conn.cursor()
        cursor.execute(query, query_exe_inputs)
        all_messages = cursor.fetchall()
        return all_messages        
    
    def fetch_groupchat(self, name):
        '''
        cache_roomnames = 'chat123456789'
        fetches all messages from the iphone backup directory
        using the supplied query file
        :return: iterable of all messages
        '''
        query_exe_inputs = dict()
        query_exe_inputs['name'] = name

        whereclause = "cache_roomnames = :name"
        query = self._read('select_msg_from_roomname.sql')
        query = Template(query).safe_substitute(dict(whereclause=whereclause))

        conn = sqlite3.connect(self._message_db_file)
        # conn.execute(f'ATTACH DATABASE [{self._contacts_db_file}] AS contacts')

        cursor = conn.cursor()
        cursor.execute(query, query_exe_inputs)
        all_messages = cursor.fetchall()
        return all_messages
    

    def _read(self, file) -> str:
        '''
        reads the input file, return the text
        '''
        with open(file, 'r') as f:
            output = f.read()
        return output


class DocumentWriter:
    def __init__(self,
                 output_file,
                 template_file,
                 ):
        self.output = output_file
        self.template = template_file

    video_mime = {
        ".mov": "video/quicktime",
        ".mp4": "video/mp4"
    }


    def _append_output(self, html):
        '''
        appends the html text to the output file
        '''
        with open(self.output, encoding='utf-8', mode='a') as f:
            f.write(html)


    def _write_output(self, html):
        '''
        writes the html text to the output file
        (will clear anything already in the file
        '''
        with open(self.output, encoding='utf-8', mode='w') as f:
            f.write(html)


    def write_intro(self, msg_to, msg_from):
        '''
        writes the intro html to the output file

        :template_path: path to the template html file
                        will be used to find header info
        :header_inputs: string template substitiion will be used
                        to put some info in the headers
        '''
        intro_inputs = dict(msg_to=msg_to, msg_from=msg_from)

        template = _get_document_section(self.template,
                                     'template:intro-start',
                                     'template:intro-end')

        intro = Template(template).safe_substitute(intro_inputs)
        self._write_output(intro)


    def write_end(self, closer_inputs=dict()):
        '''
        writes the closing html to the output file
        '''
        template = _get_document_section(self.template,
                                     'template:closer-start',
                                     'template:closer-end')

        closer = Template(template).safe_substitute(closer_inputs)
        self._append_output(closer)


    def write_message(self, msg:iMessage):
        '''
        writes a message to the main file
        '''
        self._append_output(self.make_message_html(msg))


    def make_message_html(self, msg:iMessage):
        '''
        makes the html for a given message
        '''
        html = ''
        if msg.has_attachment:
            media = self._make_media_html(msg)
            html = html + media
        if msg.has_text:
            text = self._make_text_html(msg)
            html = html + text
        return html


    def _make_text_html(self, message:iMessage) -> str:
        '''
        builds the message html for normal text
        :message: the message to insert
        :return: html string
        '''
        if message.is_from_me:
            section_start = 'template:text-myMessage-start'
            section_end= 'template:text-myMessage-end'

        else:
            section_start = 'template:text-fromThem-start'
            section_end= 'template:text-fromThem-end'

        template = _get_document_section(self.template,
                                            section_start,
                                            section_end)

        html = Template(template).safe_substitute(text = message.text,
                                                name = message.firstname,
                                                date = message.date,
                                                time = message.time)
        return html


    def _make_media_html(self, message:iMessage) -> str:
        '''
        builds the message html for normal text
        :message: the message to insert
        :return: html string
        '''
        relative_media_path = message.attachment_filename.relative_to(self.output.parent)

        filetype = Path(relative_media_path).suffix.lower().strip()
        mime = self.video_mime.get(filetype)

        section = "template:media-"

        if mime is not None:
            section += "video-"
        
        section += "myMessage-" if message.is_from_me else "fromThem-"

        section_start = section + "start"
        section_end = section + "end"

        template = _get_document_section(self.template,
                                         section_start,
                                         section_end)


        html = Template(template).safe_substitute(media_path = str(relative_media_path),
                                                  name = message.firstname,
                                                  date = message.date,
                                                  time = message.time,
                                                  mime = mime)
        return html



def _get_document_section(file_path, start:str, end:str):
    '''
    :return: a section of a document defined by custom annotation strings
    :path: path to document
    :start: annotation string marking the start of the section
    :end: annotation string marking the end of the section
    '''
    with open(file_path, 'r') as f:
        section = ''
        in_section = False

        for line in f.readlines():
            if start in line:
                in_section = True
                continue

            if end in line:
                in_section = False
                break

            if in_section:
                section = section + line
    
    return section


class iOSContacts:
    def __init__(self, iphone_backup_dir, query_file, firstname, lastname):
        self.iphone_backup_dir = iphone_backup_dir
        self.query_file = query_file
        self._query_inputs = dict(first=firstname, last=lastname)
        self._contacts_db_filename = str(iphone_backup_dir / '31' / '31bb7ba8914766d4ba40d6dfb6113c8b614be442')


    def _read(self, file):
        '''
        reads the text from the input file
        '''
        with open(file, 'r') as f:
            output = f.read()
        return output


    def get_all_contacts(self):
        '''
        returns an iterable of all contacts in the iphone backup
        and the values associated with it
        '''
        conn = sqlite3.connect(self._contacts_db_filename)
        cursor = conn.cursor()
        cursor.execute('SELECT First, Last, value FROM ABMultiValue, ABPerson WHERE record_id = ROWID AND value is not null order by first')
        entries = cursor.fetchall()
        return entries
