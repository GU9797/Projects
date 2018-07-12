# This file uses the tables with all scraped data and prepares them for
# record linkage.
# It then uses the matched IDs to combine all the tables into one table, mcp.

import sqlite3

conn = sqlite3.connect("with_coords")
c = conn.cursor()

# if re-running:
# c.executescript('''DROP TABLE cct_rl;
#                     DROP TABLE mcp;
#                     DROP TABLE cp;
#                     DROP TABLE help;
#                     DROP TABLE mac_working;
#                     DROP TABLE ma_rl;
#                     DROP TABLE pp_rl;
#                     DROP TABLE cct_working;''')



# Prepare Propublica table for record linkage:
c.executescript('''CREATE TABLE pp_rl
        (ppID int,
        name varchar(1000),
        revenue varchar(20),
        pp_text varchar(1000),
        coords varchar(50));

    INSERT INTO pp_rl (ppID, name, revenue, pp_text, coords)
    SELECT rowid, name, revenue, pp_text, coords
    FROM pp_all
    WHERE active="True";
    ''')


# Prepare the Chicago Community Trust table for record linkage:
c.executescript('''CREATE TABLE cct_working
        AS SELECT org_id, name, description
        FROM cct_orgs_all;

    ALTER TABLE cct_working ADD text_dump;

    ALTER TABLE cct_working ADD funders;
    ''')

for row in c.execute('''SELECT org_id, name, description
        FROM cct_working;''').fetchall():
    all_text = row[1] + ' ' + row[2] # concatenate all text
    working_id = row[0]
    grant_list = []
    # find all the grants an organization received
    for grant in c.execute('''SELECT cct_grants_all.funder
            FROM cct_grants_all JOIN cct_working
            ON cct_grants_all.org_id = cct_working.org_id
            WHERE cct_working.org_id = ?;''', [working_id]).fetchall():
        grant_list.append(grant[0])
    grant_string = ",".join(grant_list) # grants joined with commas
    args = [all_text, grant_string, row[0]]

    c.execute('''UPDATE cct_working
        SET text_dump = ?, funders = ?
        WHERE org_id = ?;''', args)

c.executescript('''CREATE TABLE cct_rl
        (cctID int,
        name varchar(1000),
        funders varchar(500),
        text_dump varchar(2000));

    INSERT INTO cct_rl (cctID, name, funders, text_dump)
    SELECT org_id, name, funders, text_dump
    FROM cct_working;
    ''')


# Prepare the MacArthur Foundation table for record linkage:
c.executescript('''CREATE TABLE mac_working
        AS SELECT rowid, name, description
        FROM mac_all;

    ALTER TABLE mac_working ADD text_dump;

    ALTER TABLE mac_working ADD funders;

    ''')

for row in c.execute('''SELECT rowid, name, description
        FROM mac_working;''').fetchall():
    all_text = row[1] + " " + row[2] # concatenate all text
    # The MacArthur Foundation is the grant-giver for all of these organizations
    args = [all_text, 'MacArthur Foundation', row[0]]
    c.execute('''UPDATE mac_working
            SET text_dump = ?, funders = ?
            WHERE rowid = ?;''', args)

c.executescript('''CREATE TABLE ma_rl
        (maID int,
        name varchar(1000),
        funders varchar(500),
        text_dump varchar(2000));

    INSERT INTO ma_rl (maID, name, funders, text_dump)
    SELECT rowid, name, funders, text_dump
    FROM mac_working;
    ''')


# Record Linkage Tables:

# pp_rl: ppid | name | revenue | pp_text | coords
# cct_rl: cctID | name | funders | text_dump
# mac_rl: macID | name | funders | text_dump



# Record Linkage

# join ppID and cctID from match table; this code replicates a FULL OUTER JOIN
c.execute('''CREATE TABLE help AS
SELECT p.*, m.cctID
FROM pp_rl p
LEFT JOIN cct_pp_matches m
USING (ppID)
UNION ALL
SELECT p.*, m.cctID
FROM cct_pp_matches m
LEFT JOIN pp_rl p
USING (ppID)
WHERE m.ppID IS NULL;''')

# add data from cct_rl
c.executescript('''CREATE TABLE cp AS
SELECT h.ppID, h.name, h.revenue, h.pp_text, h.coords, c.cctID, c.name,
    c.funders, c.text_dump
FROM help h
LEFT JOIN cct_rl c
USING (cctID)
UNION ALL
SELECT h.ppID, h.name, h.revenue, h.pp_text, h.coords, c.cctID, c.name,
    c.funders, c.text_dump
FROM cct_rl c
LEFT JOIN help h
USING (cctID)
WHERE h.cctID IS NULL;

DROP TABLE help;''')


# Now the same for pp and ma:
c.executescript('''CREATE TABLE help AS
SELECT cp.*, m.maID
FROM cp
LEFT JOIN ma_pp_matches m
USING (ppID)
UNION ALL
SELECT cp.*, m.maID
FROM ma_pp_matches m
LEFT JOIN cp
USING (ppID)
WHERE m.ppID IS NULL;

CREATE TABLE mcp AS
SELECT h.ppID, h.name, h.revenue, h.pp_text, h.cctID, h.funders, h.text_dump,
    h.coords, h."name:1", ma.text_dump, ma.maID, ma.funders, ma.name
FROM help h
LEFT JOIN ma_rl ma
USING (maID)
UNION ALL
SELECT h.ppID, h.name, h.revenue, h.pp_text, h.cctID, h.funders, h.text_dump,
    h.coords, h."name:1", ma.text_dump, ma.maID, ma.funders, ma.name
FROM ma_rl ma
LEFT JOIN help h
USING (maID)
WHERE h.maID IS NULL;
''')

# Use the final mcp file and combine funders, text dump, name
c.executescript('''ALTER TABLE mcp ADD all_text;

    ALTER TABLE mcp ADD all_funders;

    ALTER TABLE mcp ADD final_name''')

for row in c.execute('''SELECT text_dump, "text_dump:1", funders, "funders:1",
        name, "name:1", "name:2", rowid
        FROM mcp;''').fetchall():

    cct_text = row[0]
    ma_text = row[1]
    cct_grants = row[2]
    ma_grants = row[3]
    ppname = row[4]
    cctname = row[5]
    maname = row[6]


    if cct_text and ma_text:
        all_text = cct_text + " " + ma_text
    elif cct_text:
        all_text = cct_text
    elif ma_text:
        all_text = ma_text
    else:
        all_text = ''

    if cct_grants and ma_grants:
        all_funders = cct_grants + "," + ma_grants
    elif cct_text:
        all_funders = cct_grants
    elif ma_grants:
        all_funders = ma_grants
    else:
        all_funders = ''


    if ppname:
        official_name = ppname
    elif cctname:
        official_name = cctname
    elif maname:
        official_name = maname
    else:
        official_name = ''

    args = [all_text, all_funders, official_name, row[7]]
    c.execute('''UPDATE mcp
            SET all_text = ?, all_funders = ?, final_name = ?
            WHERE rowid = ?;''', args)

c.executescript('''DROP TABLE cct_rl;
                    DROP TABLE cp; DROP TABLE help;
                    DROP TABLE mac_working;
                    DROP TABLE ma_rl;
                    DROP TABLE pp_rl;
                    DROP TABLE cct_working;''')

conn.commit()
conn.close()
