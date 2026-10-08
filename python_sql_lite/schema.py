sql_create_guests_table = """
    CREATE TABLE guests (
        id INTEGER PRIMARY KEY,
        first TEXT NOT NULL,
        last TEXT NOT NULL,
        relation TEXT CHECK (relation IN (
            'mother', 'father', 'sister', 'brother', 'grandmother', 'grandfather',
            'aunt', 'uncle', 'cousin', 'niece', 'nephew',
            'friend', 'coworker', 'neighbor', 'other'
        )), -- relation to the bride or groom; family = mother, father, sister, brother, grandmother, grandfather, aunt, uncle, cousin, niece, nephew
        bride_side INTEGER NOT NULL DEFAULT 0 CHECK (bride_side IN (0, 1)), -- 1 if the guest is a bride-side guest (family OR friend)
        groom_side INTEGER NOT NULL DEFAULT 0 CHECK (groom_side IN (0, 1)) -- 1 if the guest is a groom-side guest (family OR friend)
    );
"""

sql_create_wedding_party_table = """
    CREATE TABLE wedding_party (
        guest_id INTEGER PRIMARY KEY,
        role TEXT NOT NULL CHECK (role IN (
            'maid of honor', 'best man', 'bridesmaid', 'groomsman',
            'flower girl', 'ring bearer', 'officiant'
        )),
        FOREIGN KEY (guest_id) REFERENCES guests(id)
    );
"""

sql_create_gifts_table = """
    CREATE TABLE gifts (
        id INTEGER PRIMARY KEY,
        type TEXT NOT NULL,
        guest_id INTEGER NOT NULL,
        event_id INTEGER,  -- NULL when the gift was shipped, not given at an event
        FOREIGN KEY (guest_id) REFERENCES guests(id),
        FOREIGN KEY (event_id) REFERENCES events(id)
    );
"""

sql_create_events_table = """
    CREATE TABLE events (
        id INTEGER PRIMARY KEY,
        event_name TEXT NOT NULL
    );
"""

sql_create_rsvps_table = """
    CREATE TABLE rsvps (
        event_id INTEGER NOT NULL,
        guest_id INTEGER NOT NULL,
        rsvp TEXT NOT NULL DEFAULT 'pending' CHECK (rsvp IN ('yes', 'no', 'pending')),
        attended INTEGER NOT NULL DEFAULT 0 CHECK (attended IN (0, 1)),
        PRIMARY KEY (event_id, guest_id),
        FOREIGN KEY (event_id) REFERENCES events(id),
        FOREIGN KEY (guest_id) REFERENCES guests(id)
    );
"""
