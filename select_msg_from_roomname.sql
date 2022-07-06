SELECT 
    m.rowid as RowID,
    h.id AS UniqueID, 
    m.is_from_me as Is_From_Me,

    CASE WHEN date > 0 THEN
        time(date / 1000000000 + 978307200, 'unixepoch', 'localtime')
        ELSE NULL
    END AS Time,
    
    CASE WHEN date > 0 THEN
        strftime('%Y%m%d', date / 1000000000 + 978307200, 'unixepoch', 'localtime')
    END AS Date,

    CASE WHEN date > 0 THEN
        date / 1000000000 + 978307200
    END AS Epoch,

    text as Text,
    a.filename AS AttachmentPath

    FROM message m
    LEFT JOIN handle h ON h.rowid = m.handle_id
    LEFT JOIN message_attachment_join maj ON maj.message_id = m.rowid
    LEFT JOIN attachment a ON a.rowid = maj.attachment_id

    WHERE $whereclause

    ORDER BY Date, Time
