
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
    def __init__(self, msg):
        self.raw_message = msg
        self.text = msg[6]
        self.time = msg[3]
        self.date = format_date(msg[4])
        self.uniqueID = msg[1]

        if msg[2] == 1:
            self.is_from_me = True
            self.name = 'Me'
        else:
            self.is_from_me = False
            self.name = self.uniqueID

        if msg[7] is not None:
            self.has_attachment = True
            self.attachment_src_path = self._get_attachment_source(msg[7])
            self.attachment_filename = self._get_attachment_filename(msg[7])
        else:
            self.has_attachment = False
            
        if msg[6] is not None:
            self.has_text = True
        else:
            self.has_text = False


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
        if ext.lower() in ['jpg', 'png', 'mov', 'jpeg', 'gif']:
            domainpath = 'MediaDomain-' + raw_path[2:] # create the domain path that will be hashed
            filename = sha1(domainpath.encode('utf-8')).hexdigest() # create the SHA1 hash (which is the file name)
            dir = filename[:2] # the first two digets of the filename are the directory name
            return Path(dir, filename) # create an file path to the attachment
        else:
            print(f'skipped over {ext} type file')
            #raise ValueError('FILE NAME I DON\'T KNOW HOW TO DEAL WITH WHAT DO I DO')
        

class MessageBackupReader:
    def __init__(self, iphone_backup_dir, query_file, contact_number, contact_email):
        self.iphone_backup_dir = iphone_backup_dir
        self.query_file = query_file
        self.contact_info = (contact_number, contact_email)

    
    def fetch_all(self):
        '''
        fetches all messages from the iphone backup directory
        using the supplied query file
        '''
        return self._fetch_all_messages(self.iphone_backup_dir, self.contact_info)


    def _fetch_all_messages(self, iphone_backup_folder, contact_info):
        '''
        opens up the sqlite files and reads all messages
        :param iphone_backup_folder: path to the iphone backup folder
                                     (does not include path to messages)
        :param contact_info: tuple of contact info you wish to retrieve messages for
        :return: iterable of all messages
        '''
    
        connection_path = str(iphone_backup_folder / '3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28')

        conn = sqlite3.connect(connection_path)

        cursor = conn.cursor()

        query = self._create_sql_query()

        cursor.execute(query, contact_info)

        all_messages = cursor.fetchall()

        return all_messages
    

    def _create_sql_query(self) -> str:
        '''
        reads the sql query
        has the "?"s built into it -- that's not very flexible
        '''
        with open(self.query_file, 'r') as f:
            query = f.read()

        return query


class DocumentWriter:
    def __init__(self,
                 output_file,
                 template_file,
                 intro_inputs = dict(),
                 closer_inputs = dict()
                 ):
        self.output = output_file
        self.template = template_file
        self.intro_inputs = intro_inputs
        self.closer_inputs = closer_inputs


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


    def write_intro(self):
        '''
        writes the intro html to the output file

        :template_path: path to the template html file
                        will be used to find header info
        :header_inputs: string template substitiion will be used
                        to put some info in the headers
        '''
        template = _get_document_section(self.template,
                                     'template:intro-start',
                                     'template:intro-end')

        intro = Template(template).safe_substitute(self.intro_inputs)
        self._write_output(intro)


    def write_closer(self):
        '''
        writes the closing html to the output file
        '''
        template = _get_document_section(self.template,
                                     'template:closer-start',
                                     'template:closer-end')

        closer = Template(template).safe_substitute(self.closer_inputs)
        self._append_output(closer)


    def write_message(self, msg:iMessage):
        '''
        writes a message to the main file
        '''
        if msg.has_attachment:
            html = self._make_media_html(msg)
            self._append_output(html)

        if msg.has_text:
            html = self._make_text_html(msg)
            self._append_output(html)

        # copy attachment if needed


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
                                                name = message.name,
                                                date = message.date,
                                                time = message.time)
        return html


    def _make_media_html(self, message:iMessage) -> str:
        '''
        builds the message html for normal text
        :message: the message to insert
        :return: html string
        '''
        if message.is_from_me:
            section_start = 'template:media-myMessage-start'
            section_end= 'template:media-myMessage-end'

        else:
            section_start = 'template:media-fromThem-start'
            section_end= 'template:media-fromThem-end'

        template = _get_document_section(self.template,
                                            section_start,
                                            section_end)

        html = Template(template).safe_substitute(media_path = message.attachment_filename,
                                                name = message.name,
                                                date = message.date,
                                                time = message.time)
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

        self.query_inputs = dict(first=firstname, last=lastname)

        self._contacts_db_filename = Path('31', '31bb7ba8914766d4ba40d6dfb6113c8b614be442')


    def _make_query(self):
        '''
        reads the query from the query file
        '''
        with open(self.query_file, 'r') as f:
            query = f.read()

        return query


    def _query_contacts(self):
        '''
        connects to the contacts database and generates all contacts
        :return: iterable of contacts
        '''
    
        connection_path = str(self.iphone_backup_folder / self._contacts_db_filename)

        conn = sqlite3.connect(connection_path)

        cursor = conn.cursor()

        query = self._make_query()

        cursor.execute(query, self.query_inputs)

        entries = cursor.fetchall()

        return entries