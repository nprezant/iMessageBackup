# -*- coding: utf-8 -*

# works for iOS 10.2

import sqlite3
from hashlib import sha1
from shutil import copy2
import os

def FormatDate(dt, in_type):
    if in_type=='YYYYMMDD':
        return dt[4:6] + '/' + dt[6:8] + '/' + dt[0:4]

BACKUP_PATH = 'C:/Users/Noah/AppData/Roaming/Apple Computer/MobileSync/Backup/3abca6c8b1917981e5c1d8407896df036573f510'
DST_PATH = 'C:/Users/Noah/Documents/Lauren/iOSBackup/iMessageBackup'

conn = sqlite3.connect('sqlite/2018-09-21/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28')

c = conn.cursor()

# (contact phone number, contact email)
contact_info = ('%1234567890%', '%contactname@gmail.com%')
c.execute("""SELECT 
m.rowid as RowID,
h.id AS UniqueID, 
m.is_from_me as Is_From_Me,
CASE 
	WHEN date > 0 then TIME(date + 978307200, 'unixepoch', 'localtime')
	ELSE NULL
END as Time,
CASE 
	WHEN date > 0 THEN strftime('%Y%m%d', date + 978307200, 'unixepoch', 'localtime')
	ELSE NULL
END as Date, 
CASE 
	WHEN date > 0 THEN date + 978307200
	ELSE NULL
END as Epoch, 
text as Text,
a.filename AS AttachmentPath

FROM message m
LEFT JOIN handle h ON h.rowid = m.handle_id
LEFT JOIN message_attachment_join maj ON maj.message_id = m.rowid
LEFT JOIN attachment a ON a.rowid = maj.attachment_id

WHERE UniqueID like ? OR UniqueID like ? AND m.cache_roomnames is null

ORDER BY Date, Time""", contact_info)

with open(DST_PATH + '/' + '_export.html', encoding='utf-8', mode='w') as f:
    # print header
    f.write("""<!DOCTYPE html><head><meta charset="utf-8" />
    <link rel="shortcut icon" href="img/like.png"/>
    <title>Lauren&Noah -- Archives</title>
    <style type="text/css">
    *{margin: 0;padding: 0; font:normal 12px "Lucida Grande", "Lucida Sans Unicode", "Arial";color:#333;}
    body{ background: #eee}
    img{border: none;max-width:320px;}
    .wrap{ width: 640px; margin: 0 auto;}
    .top{ width: 100%; height: 42px; background: #3dc79c; text-align: center; font-size: 18px; color: #fff; font-weight: bolder; line-height: 42px;}
    .cont{ background: #fff; padding: 18px; min-height: 300px; float: left;}
    .cont h1{ width: 600px; height: 32px; font-size:20px; color: #000;  border-bottom: 1px solid #e5e5e5;}
    .date{ font-size: 14px; color: #919191; text-align: center;margin: 20px 0 5px 0;}
    .imessage{font-size: 14px;color: #919191;text-align: center;margin: 20px 0 -10px 0;}
    .right{ float: right;}
    .left{ float: left;}
    .left_top{ width:14px;background:url(img/left_top.png) no-repeat;}
    .right_top{ width: 14px;background:url(img/right_top.png) no-repeat;}
    .right_mid{ background:url(img/right_mid.png) repeat-y;}
    .left_bottom{background:url(img/left_bottom.png) no-repeat;}
    .right_bottom{ width: 20px; height: 14px; background:url(img/right_bottom.png) no-repeat;}
    .block_table{ width: 604px;  float: left; margin: 0 0 .5em 0;}
    .block_table tr td{ max-width: 302px;}
    .left_top2{ width:22px;background:url(img/left_top2.png) no-repeat right;}
    .right_top2{ width:14px; height:14px; background:url(img/right_top2.png) no-repeat;}
    .right_mid2{ background:url(img/right_mid2.png) repeat-y right;}
    .left_bottom2{background:url(img/left_bottom2.png) no-repeat left;  width: 22px; height: 14px; }
    .right_bottom2{background:url(img/right_bottom2.png) no-repeat; }
    .left_top3{ width:14px;background:url(img/left_top3.png) no-repeat;}
    .right_top3{ width: 14px;background:url(img/right_top3.png) no-repeat;}
    .right_mid3{ background:url(img/right_mid3.png) repeat-y;}
    .left_bottom3{background:url(img/left_bottom3.png) no-repeat;}
    .right_bottom3{ width: 20px; height: 14px; background:url(img/right_bottom3.png) no-repeat;}
    .bg_color{ background: #20a8fe; color: #fff;}
    .bg_color2{ background: #e9e9ed;}
    .bg_color3{ background: #79eb60; color: #fff;}
    </style>
    </head>""")

    # begin the body
    f.write("""<body>
    <div class='wrap'>
    <div class='cont'>
    <h1>Lauren Zitney <span style='float:right;font-size:20px;'>Noah Prezant</span></h1>
    <p class='imessage'>iMessage</p>""")

    all_records = c.fetchall()
    num_records = len(all_records)

    print('Writing messages to file...')

    n = 0
    for row in all_records:

        #if n==2000:
        #    break

        if n % 1000 == 0:
            print(f'{n}/{num_records}')

        n += 1

        # read message
        if row[6] is None:
            msg = ''
        else:
            msg = row[6]

        # read message time
        if row[3] is None:
            msgtime = ''
        else:
            msgtime = row[3]

        # read message date
        if row[4] is None:
            msgdate = ''
        else:
            msgdate = FormatDate(row[4], 'YYYYMMDD')

        # read attachment id
        if row[7] is None:
            apath = ''
            att = False
        else:
            apath = row[7]
            att_name = apath.split('/')[-1] # gets the file name, e.g. IMG_2613.PNG
            att_ext = apath.split('.')[-1] # gets the file extension, e.g. PNG
            if att_ext.lower() in ['jpg', 'png', 'mov', 'jpeg']:
                att_domainpath = 'MediaDomain-' + apath[2:] # create the domain path that will be hashed
                att_filename = sha1(att_domainpath.encode('utf-8')).hexdigest() # create the SHA1 hash (which is the file name)
                att_folder = att_filename[:2] # the first two digets of the filename are the directory name
                att_src = BACKUP_PATH + '/' + att_folder + '/' + att_filename # create an complete file path to the attachment
                att_dst_dir = DST_PATH + '/' + 'attachments'
                att_dst = att_dst_dir + '/' + att_name
                att_localpath = 'attachments' + '/' + att_name # note this string to be put into the HTML
                if not os.path.isdir(att_dst_dir):
                    os.mkdir(att_dst_dir)
                copy2(att_src, att_dst)
                att = True # this message has an attachment
            else:
                att = False

        f.write("""<p class='date'>""")
        f.write(f'{msgdate}::{msgtime}')
        f.write('</p>')
        f.write("""<div class='block_table'>
        <div class='block_table'><div class='block_table'>
        """)

        # if the message is from me
        if row[2]==1:
            f.write("""<table class='right' width='auto' height='auto' border='0' cellpadding='0' cellspacing='0'>
            <tr><td class='left_top'></td>
            <td width='auto' class='bg_color' height='12'></td>
            <td class='right_top'></td></tr>
            <tr><td height='auto'  class='bg_color'></td>
            <td  class='bg_color' maxwidth='330'>""")
            if att: f.write('<img src = "' + att_localpath + '" style="width: 100%;"/>')
            f.write(msg)
            f.write("""</td>
            <td  class='right_mid' width='14'></td></tr>
            <tr><td class='left_bottom'></td>
            <td  class='bg_color'></td>
            <td class='right_bottom'></td></tr></table>
            </div></div></div>""")
        # if the message is not from me
        elif row[2]==0:
            f.write("""<table class='left' width='auto' height='auto' border='0' cellpadding='0' cellspacing='0'>
            <tr><td class='left_top2'></td>
            <td width='auto' class='bg_color2' height='12'></td>
            <td class='right_top2'></td></tr>
            <tr><td height='auto'  class='right_mid2'></td>
            <td  class='bg_color2' maxwidth='330'>""")
            if att: f.write('<img src = "' + att_localpath + '" style="width: 100%;"/>')
            f.write(msg)
            f.write("""</td>
            <td  class='bg_color2' width='14'></td></tr>
            <tr><td class='left_bottom2'></td>
            <td  class='bg_color2'></td>
            <td class='right_bottom2'></td></tr></table>
            </div></div></div>""")

    # end the body
    f.write("""</div>
    </div>
    </body></html>""")

conn.close()
