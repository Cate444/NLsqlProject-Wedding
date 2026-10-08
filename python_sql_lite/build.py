import os

from db import create_table, create_connection
from schema import *

DATABASE = "./wedding.db"

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

# (id, first, last, relation, bride_side, groom_side)
GUESTS = [
    # Bride's side of the wedding party
    (1, 'Sydney', 'Nielson', 'sister', 1, 0),
    (2, 'Eva', 'Renfro', 'sister', 1, 0),
    (3, 'Lauren', 'Murphy', 'sister', 1, 0),
    (4, 'Ashleigh', 'Heafen', 'sister', 1, 0),
    (5, 'Meg', 'Mott', 'friend', 1, 0),
    (6, 'Rachel', 'Mott', 'friend', 1, 0),
    (7, 'Jackie', 'Barton', 'friend', 1, 0),
    (8, 'Natalee', 'Dong', 'friend', 1, 0),
    (9, 'Ella', 'Callister', 'friend', 1, 0),
    # Groom's side of the wedding party
    (10, 'Tyler', 'Heaton', 'friend', 0, 1),
    (11, 'Andrew', 'Price', 'friend', 0, 1),
    (12, 'Kyle', 'Motley', 'brother', 0, 1),
    (13, 'Sean', 'Motley', 'brother', 0, 1),
    (14, 'Kade', 'Motley', 'brother', 0, 1),
    (15, 'Luke', 'Roberts', 'friend', 0, 1),
    (16, 'Tyson', 'Vanwagner', 'friend', 0, 1),
    # Kids
    (17, 'Jackie', 'Murphy', 'niece', 1, 0),
    (18, 'Emerson', 'Murphy', 'nephew', 1, 0),
    # Parents
    (19, 'Ty', 'Allen', 'father', 1, 0),
    (20, 'Heather', 'Allen', 'mother', 1, 0),
    (21, 'Scott', 'Motley', 'father', 0, 1),
    (22, 'Carrie', 'Motley', 'mother', 0, 1),
    # DUMMY guests (made up for testing)
    (23, 'Linda', 'Allen', 'grandmother', 1, 0),
    (24, 'Robert', 'Allen', 'grandfather', 1, 0),
    (25, 'Karen', 'Jensen', 'aunt', 1, 0),
    (26, 'Mike', 'Jensen', 'uncle', 1, 0),
    (27, 'Brooke', 'Jensen', 'cousin', 1, 0),
    (28, 'Diane', 'Motley', 'grandmother', 0, 1),
    (29, 'Paul', 'Hansen', 'uncle', 0, 1),
    (30, 'Susan', 'Hansen', 'aunt', 0, 1),
    (31, 'Jake', 'Hansen', 'cousin', 0, 1),
    (32, 'Megan', 'Carter', 'coworker', 1, 0),
    (33, 'Chris', 'Nguyen', 'coworker', 0, 1),
    (34, 'Amy', 'Peterson', 'neighbor', 1, 1),
    (35, 'Dan', 'Peterson', 'neighbor', 1, 1),
    (36, 'Olivia', 'Brooks', 'friend', 1, 1),
]

# (guest_id, role)
WEDDING_PARTY = [
    (1, 'maid of honor'),
    (2, 'maid of honor'),
    (3, 'bridesmaid'),
    (4, 'bridesmaid'),
    (5, 'bridesmaid'),
    (6, 'bridesmaid'),
    (7, 'bridesmaid'),
    (8, 'bridesmaid'),
    (9, 'bridesmaid'),
    (10, 'best man'),
    (11, 'groomsman'),
    (12, 'groomsman'),
    (13, 'groomsman'),
    (14, 'groomsman'),
    (15, 'groomsman'),
    (16, 'groomsman'),
    (17, 'flower girl'),
    (18, 'ring bearer'),
]

# (id, event_name)
EVENTS = [
    (1, 'Family Bridal Shower'),
    (2, 'Friend Bridal Shower'),
    (3, 'Bachelorette Party'),
    (4, 'Bachelor Party'),
    (5, 'Ceremony'),
    (6, 'Reception'),
]

# (event_id, guest_id, rsvp, attended)
RSVPS = [
    # Family Bridal Shower: mothers and sisters
    (1, 1, 'yes', 1),
    (1, 2, 'yes', 1),
    (1, 3, 'yes', 1),
    (1, 4, 'yes', 0),       # dummy: said yes, didn't come
    (1, 20, 'yes', 1),
    (1, 22, 'no', 0),       # dummy: declined
    # Friend Bridal Shower: bridesmaids and maids of honor
    (2, 1, 'yes', 1),
    (2, 2, 'yes', 1),
    (2, 3, 'no', 0),        # dummy
    (2, 4, 'yes', 1),
    (2, 5, 'yes', 1),
    (2, 6, 'yes', 1),
    (2, 7, 'yes', 0),       # dummy
    (2, 8, 'yes', 1),
    (2, 9, 'pending', 0),   # dummy: never responded
    # Bachelorette Party: bridesmaids and maids of honor
    (3, 1, 'yes', 1),
    (3, 2, 'yes', 1),
    (3, 3, 'yes', 1),
    (3, 4, 'yes', 1),
    (3, 5, 'yes', 1),
    (3, 6, 'no', 0),        # dummy
    (3, 7, 'yes', 1),
    (3, 8, 'yes', 1),
    (3, 9, 'yes', 1),
    # Bachelor Party: best man and groomsmen
    (4, 10, 'yes', 1),
    (4, 11, 'yes', 1),
    (4, 12, 'yes', 1),
    (4, 13, 'yes', 0),      # dummy
    (4, 14, 'yes', 1),
    (4, 15, 'no', 0),       # dummy
    (4, 16, 'yes', 1),
]

# Ceremony and Reception: every guest is invited. Default is ('yes', attended);
# these dummy exceptions override it. guest_id: (ceremony, reception)
CEREMONY_RECEPTION_EXCEPTIONS = {
    27: (('pending', 0), ('pending', 0)),  # never responded
    31: (('yes', 0), ('yes', 1)),          # missed the ceremony, came to the reception
    33: (('no', 0), ('no', 0)),            # declined both
}
for guest_id, *_ in GUESTS:
    ceremony, reception = CEREMONY_RECEPTION_EXCEPTIONS.get(guest_id, (('yes', 1), ('yes', 1)))
    RSVPS.append((5, guest_id, *ceremony))
    RSVPS.append((6, guest_id, *reception))

# (id, type, guest_id, event_id) — all DUMMY gifts; event_id None = shipped
GIFTS = [
    (1, 'towel set', 1, 1),
    (2, 'cookbook', 2, 1),
    (3, 'Dutch oven', 3, 1),
    (4, 'quilt', 20, 1),
    (5, 'candle set', 5, 2),
    (6, 'wine glasses', 6, 2),
    (7, 'cutting board', 8, 2),
    (8, 'throw blanket', 9, 2),
    (9, 'picture frame', 7, None),
    (10, 'cooler', 10, 4),
    (11, 'cash', 19, 6),
    (12, 'cash', 21, 6),
    (13, 'recipe book', 23, 6),
    (14, 'KitchenAid mixer', 25, 6),
    (15, 'gift card', 26, 6),
    (16, 'gift card', 32, 6),
    (17, 'air fryer', 34, 6),
    (18, 'cash', 11, 6),
    (19, 'toaster', 33, None),
]


def insert_rows(conn, table, rows):
    """Insert a list of tuples into a table using a parameterized query."""
    if not rows:
        return
    placeholders = ", ".join("?" * len(rows[0]))
    cur = conn.cursor()
    cur.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
    conn.commit()


def main():
    # Start fresh each build so CREATE TABLE / INSERT don't collide with old data
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    conn = create_connection(DATABASE)

    # Parent tables first, so foreign keys have something to point to
    create_table(conn, sql_create_guests_table)
    insert_rows(conn, "guests", GUESTS)
    create_table(conn, sql_create_wedding_party_table)
    insert_rows(conn, "wedding_party", WEDDING_PARTY)
    create_table(conn, sql_create_events_table)
    insert_rows(conn, "events", EVENTS)
    create_table(conn, sql_create_gifts_table)
    insert_rows(conn, "gifts", GIFTS)
    create_table(conn, sql_create_rsvps_table)
    insert_rows(conn, "rsvps", RSVPS)

    print("Database build successful!")


if __name__ == "__main__":
    main()
