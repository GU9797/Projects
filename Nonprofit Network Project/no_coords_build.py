# This file initializes all the tables for the scraped data.
# The tables are populated using the sqlite3 command line.

import sqlite3

conn = sqlite3.connect("with_coords")
c = conn.cursor()

# initialize all the tables
c.executescript('''CREATE TABLE pp_all
        (name varchar(1000),
        address varchar(1000), 
        pp_text varchar(1000),
        active varchar(10),
        latest_year varchar(10),
        info_year varchar(10),
        revenue int,
        expenses int,
        assets int,
        liabilities int,
        contributions_rev int,
        program_service_rev int,
        coords varchar(50));

    CREATE TABLE cct_orgs_all (org_id int,
        name varchar(1000),
        description varchar(1000));

    CREATE TABLE cct_grants_all (org_id int,
        funder varchar(1000),
        amount varchar(20),
        grant_year varchar(10),
        purpose varchar(500));

    CREATE TABLE mac_all (name varchar(1000),
        amount varchar(20),
        grant_year varchar(10),
        duration varchar(50),
        description varchar(1000));

    CREATE TABLE cct_pp_matches (cctID int, ppID int);

    CREATE TABLE ma_pp_matches (maID int, ppID int);

''')

conn.commit()
conn.close()



# populate at the command line:
'''
sqlite3 with_coords
    .mode csv
    .separator "|"
    .import coordinates2.csv pp_all
    .import mac_grants+descriptions.csv mac_all
    .separator ","
    .import all_pages_orgs.csv cct_orgs_all
    .import all_pages_grants.csv cct_grants_all
    .import matches_pp_cct.csv cct_pp_matches
    .import matches_pp_ma.csv ma_pp_matches
'''
