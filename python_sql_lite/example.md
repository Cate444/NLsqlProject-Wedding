Question: Who are the bride's sisters?
SQL: SELECT first, last
FROM guests
WHERE relation = 'sister'
  AND bride_side = 1;
Rows: [('Sydney', 'Nielson'), ('Eva', 'Renfro'), ('Lauren', 'Murphy'), ('Ashleigh', 'Heafen')]
Answer: The bride’s sisters are Sydney Nielson, Eva Renfro, Lauren Murphy, and Ashleigh Heafen.
Question: Who RSVP'd yes to the bachelor party but didn't show up?
SQL: SELECT g.first, g.last
FROM guests AS g
JOIN rsvps AS r ON r.guest_id = g.id
JOIN events AS e ON e.id = r.event_id
WHERE e.event_name = 'bachelor party'
  AND r.rsvp = 'yes'
  AND r.attended = 0;
Rows: []
Answer: No one matched those criteria.
Question: What gifts did the groom's family give?
SQL: SELECT g.first, g.last, gifts.type
FROM gifts
JOIN guests AS g ON gifts.guest_id = g.id
WHERE g.groom_side = 1;
Rows: [('Tyler', 'Heaton', 'cooler'), ('Scott', 'Motley', 'cash'), ('Amy', 'Peterson', 'air fryer'), ('Andrew', 'Price', 'cash'), ('Chris', 'Nguyen', 'toaster')]
Answer: The groom’s side gave a cooler from Tyler Heaton, cash from Scott Motley, an air fryer from Amy Peterson, cash from Andrew Price, and a toaster from Chris Nguyen.
Question: Delete all the guests
SQL: DELETE FROM guests;
Query failed: Only SELECT queries are allowed


(.venv) (base) cateallen@MacBook-Pro-341 python_sql_lite % ../../.venv/bin/python main.py --strategy cross_domain --query "Is Scott going to be at the reception?" 
Question: Is Scott going to be at the reception?
SQL: SELECT EXISTS (
    SELECT 1
    FROM guests g
    JOIN rsvps r ON r.guest_id = g.id
    JOIN events e ON e.id = r.event_id
    WHERE g.first = 'Scott'
      AND e.event_name = 'reception'
      AND r.rsvp = 'yes'
);
Rows: [(0,)]
Answer: No, Scott hasn’t RSVP’d yes for the reception.

(.venv) (base) cateallen@MacBook-Pro-341 python_sql_lite % ../../.venv/bin/python main.py --strategy cross_domain --query "Who is Tyler Heaton?"                  
Question: Who is Tyler Heaton?
SQL: SELECT g.id, g.first, g.last, g.relation, g.bride_side, g.groom_side, wp.role
FROM guests g
LEFT JOIN wedding_party wp ON wp.guest_id = g.id
WHERE g.first = 'Tyler' AND g.last = 'Heaton';
Rows: [(10, 'Tyler', 'Heaton', 'friend', 0, 1, 'best man')]
Answer: Tyler Heaton is a friend on the groom’s side and the best man.

(.venv) (base) cateallen@MacBook-Pro-341 python_sql_lite % ../../.venv/bin/python main.py --strategy cross_domain --query "how many brothers does the groom have?"
Question: how many brothers does the groom have?
SQL: SELECT COUNT(*) FROM guests WHERE relation = 'brother' AND groom_side = 1;
Rows: [(3,)]
Answer: The groom has 3 brothers.

(.venv) (base) cateallen@MacBook-Pro-341 python_sql_lite % ../../.venv/bin/python main.py --strategy cross_domain --query "Did anyone buy a blender? If so who?"  
Question: Did anyone buy a blender? If so who?
SQL: SELECT DISTINCT g.first, g.last
FROM guests AS g
JOIN gifts AS gi ON gi.guest_id = g.id
WHERE gi.type = 'blender';
Rows: []
Answer: No one bought a blender. Nothing matched the search.

(.venv) (base) cateallen@MacBook-Pro-341 python_sql_lite % ../../.venv/bin/python main.py --strategy cross_domain --query "Did anyone buy a toaster? If so who?"
Question: Did anyone buy a toaster? If so who?
SQL: SELECT DISTINCT g.first, g.last
FROM guests g
JOIN gifts gi ON gi.guest_id = g.id
WHERE gi.type = 'toaster';
Rows: [('Chris', 'Nguyen')]
Answer: Yes—Chris Nguyen bought a toaster.