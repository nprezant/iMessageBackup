SELECT 
    DISTINCT m.rowid as RowID,
    h.id as UniqueID, 
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
    a.filename AS AttachmentPath,
	ABPerson.First as FirstName,
	ABPerson.Last as LastName

    FROM main.message m
    LEFT JOIN main.handle h ON h.rowid = m.handle_id
    LEFT JOIN main.message_attachment_join maj ON maj.message_id = m.rowid
    LEFT JOIN main.attachment a ON a.rowid = maj.attachment_id
	LEFT JOIN contacts.ABMultiValue ABMulti ON ABMulti.value = h.id
	LEFT JOIN contacts.ABPerson ABPerson ON ABPerson.ROWID = ABMulti.record_id

    WHERE m.cache_roomnames is null $whereclause

    ORDER BY Date, Time