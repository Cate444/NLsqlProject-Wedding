# Examples

Each example shows the question, the SQL the model generated, the rows SQLite returned, and the final plain-English answer.

"Zero-shot (schema only)" is the first version of the prompt: just the `CREATE TABLE` statements and the question. Later runs added comments to the schema explaining what the columns mean.

---

## 1. Who are the bride's sisters? ✅
**Strategy:** zero-shot (schema only)

```sql
SELECT first, last
FROM guests
WHERE relation = 'sister'
  AND bride_side = 1;
```
**Rows:** `[('Sydney', 'Nielson'), ('Eva', 'Renfro'), ('Lauren', 'Murphy'), ('Ashleigh', 'Heafen')]`

**Answer:** The bride's sisters are Sydney Nielson, Eva Renfro, Lauren Murphy, and Ashleigh Heafen.

---

## 2. Who RSVP'd yes to the bachelor party but didn't show up? ❌ → ✅
**Strategy:** zero-shot (schema only)

```sql
SELECT g.first, g.last
FROM guests AS g
JOIN rsvps AS r ON r.guest_id = g.id
JOIN events AS e ON e.id = r.event_id
WHERE e.event_name = 'bachelor party'
  AND r.rsvp = 'yes'
  AND r.attended = 0;
```
**Rows:** `[]`

**Answer:** No one matched those criteria.

**What went wrong:** The logic is right, but the event is stored as `'Bachelor Party'`, and SQLite's `=` is case-sensitive for text. The model only saw the schema, not the data, so it had to guess the spelling.

**After giving the model the actual event names:**
```sql
... WHERE e.event_name = 'Bachelor Party' AND r.rsvp = 'yes' AND r.attended = 0;
```
**Rows:** `[('Sean', 'Motley')]`

**Answer:** Sean Motley RSVP'd yes to the bachelor party but didn't show up.

---

## 3. What gifts did the groom's family give? ❌ → ✅
**Strategy:** zero-shot (schema only)

```sql
SELECT g.first, g.last, gifts.type
FROM gifts
JOIN guests AS g ON gifts.guest_id = g.id
WHERE g.groom_side = 1;
```
**Rows:** `[('Tyler', 'Heaton', 'cooler'), ('Scott', 'Motley', 'cash'), ('Amy', 'Peterson', 'air fryer'), ('Andrew', 'Price', 'cash'), ('Chris', 'Nguyen', 'toaster')]`

**Answer:** The groom's side gave a cooler from Tyler Heaton, cash from Scott Motley, an air fryer from Amy Peterson, cash from Andrew Price, and a toaster from Chris Nguyen.

**What went wrong:** The model treated "groom's family" as "anyone on the groom's side," so friends, a neighbor and a coworker were included. The answer step also quietly reworded "family" to "side" instead of pointing out the mismatch.

**After adding schema comments that define which `relation` values count as family:**
```sql
SELECT gifts.type
FROM gifts
JOIN guests ON gifts.guest_id = guests.id
WHERE guests.groom_side = 1
  AND guests.relation IN ('mother', 'father', 'sister', 'brother', 'grandmother',
                          'grandfather', 'aunt', 'uncle', 'cousin', 'niece', 'nephew');
```
**Rows:** `[('cash',)]`

**Answer:** The groom's family gave cash.

The SQL is now correct, but the answer is thin: it doesn't say *who* gave the cash (Scott Motley), because the query only selected the gift type.

---

## 4. Delete all the guests 🛑 (blocked by the app)
**Strategy:** zero-shot

```sql
DELETE FROM guests;
```
**Result:** `Query failed: Only SELECT queries are allowed`

With more schema context, the model got *better* at deleting: it deleted the child tables first so the foreign keys wouldn't block it.
```sql
DELETE FROM wedding_party;
DELETE FROM gifts;
DELETE FROM rsvps;
DELETE FROM guests;
```
The model will happily write destructive SQL, so the app has to refuse anything that isn't a `SELECT`.

---

## 5. Is Scott going to be at the reception? ❌
**Strategy:** cross-domain

```sql
SELECT EXISTS (
    SELECT 1
    FROM guests g
    JOIN rsvps r ON r.guest_id = g.id
    JOIN events e ON e.id = r.event_id
    WHERE g.first = 'Scott'
      AND e.event_name = 'reception'
      AND r.rsvp = 'yes'
);
```
**Rows:** `[(0,)]`

**Answer:** No, Scott hasn't RSVP'd yes for the reception.

**What went wrong:** Scott *did* RSVP yes. This is the same capitalization problem as #2: the event is stored as `'Reception'`. Here the answer is confidently wrong rather than empty, which is worse.

---

## 6. Who is Tyler Heaton? ✅
**Strategy:** cross-domain

```sql
SELECT g.id, g.first, g.last, g.relation, g.bride_side, g.groom_side, wp.role
FROM guests g
LEFT JOIN wedding_party wp ON wp.guest_id = g.id
WHERE g.first = 'Tyler' AND g.last = 'Heaton';
```
**Rows:** `[(10, 'Tyler', 'Heaton', 'friend', 0, 1, 'best man')]`

**Answer:** Tyler Heaton is a friend on the groom's side and the best man.

It used a `LEFT JOIN`, so the query would still work for a guest who isn't in the wedding party.

---

## 7. How many brothers does the groom have? ✅
**Strategy:** cross-domain

```sql
SELECT COUNT(*) FROM guests WHERE relation = 'brother' AND groom_side = 1;
```
**Rows:** `[(3,)]`

**Answer:** The groom has 3 brothers.

---

## 8. Did anyone buy a blender? If so, who? ✅
**Strategy:** cross-domain

```sql
SELECT DISTINCT g.first, g.last
FROM guests AS g
JOIN gifts AS gi ON gi.guest_id = g.id
WHERE gi.type = 'blender';
```
**Rows:** `[]`

**Answer:** No one bought a blender. Nothing matched the search.

---

## 9. Did anyone buy a toaster? If so, who? ✅
**Strategy:** cross-domain

```sql
SELECT DISTINCT g.first, g.last
FROM guests g
JOIN gifts gi ON gi.guest_id = g.id
WHERE gi.type = 'toaster';
```
**Rows:** `[('Chris', 'Nguyen')]`

**Answer:** Yes—Chris Nguyen bought a toaster.

---

## 10. Is Scott going to be at the reception? (retest) ✅
**Strategy:** all three. This retest is #5 after adding the real event names to the prompt.

```sql
SELECT EXISTS (
    SELECT 1
    FROM guests g
    JOIN rsvps r ON r.guest_id = g.id
    JOIN events e ON e.id = r.event_id
    WHERE g.first = 'Scott'
      AND e.event_name = 'Reception'
      AND r.rsvp = 'yes'
);
```
**Rows:** `[(1,)]`

**Answer:** Yes, Scott is going to the reception.

The only change from #5 is `'reception'` → `'Reception'`, and that flipped the answer from wrong to right.

---

## 11. Did any wedding party members skip an event they RSVP'd yes to? ⚠️
**Strategy:** all three gave the same query

```sql
SELECT EXISTS (
    SELECT 1
    FROM wedding_party wp
    JOIN rsvps r ON r.guest_id = wp.guest_id
    WHERE r.rsvp = 'yes'
      AND r.attended = 0
);
```
**Rows:** `[(1,)]`

**Answer:** Yes. At least one wedding party member skipped an event they had RSVP'd yes to.

**Technically correct, but not useful.** A person asking this wants to know *who*: Ashleigh Heafen (Family Bridal Shower), Jackie Barton (Friend Bridal Shower) and Sean Motley (Bachelor Party). The model answered the literal yes/no question.
