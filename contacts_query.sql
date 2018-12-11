SELECT 
	First, Last, value 
	FROM ABMultiValue, ABPerson 
	WHERE 
		record_id = ROWID 
		AND value is not null 
		AND First like :firstname
		AND Last like :lastname
	order by first