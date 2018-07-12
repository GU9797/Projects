#NONPROFIT NETWORK(ING)

Edwin Gavis, Mike Gu, Mia Leatherman, Michelle Li

For our final CMSC122 project, we created a search engine to enable nonprofit leaders and Illinois residents interested in founding new nonprofits to find potential connections among similar existing organizations. Our original design and early prototypes involved the use of the networkx graphing library to store and compute relations between the organizations but after resurveying the data we scraped from ProPublica, the Chicago Community Trust and the MacArthur Foundation, we realized that we could further abstract the problem by instead combining weighted keyword searches with an ensemble of machine learning predictions and revenue and distance comparisons to create a single weighted score for each relevant organization, in the manner of a commercial search engine (such as Google).

Among the files submitted, those used to create the final product include:

myform/form_app/views.py -
Code to handle and respond to input from the django form.
Main project implementation.

ml_nlp.py -
Code to train and store the KMeans models used in the final implementation. Also contains code to create and print Latent Dirichlet Allocation models that helped us to understand and cateogrize all the natural language text collected, but were not themselves included in the final implementation.

matches_pp_cct.csv -
CSV file of the matches that record_linkage.py identify between nonprofits that received funding according to Chicago Community Trust and Propublica nonprofits. The file has a column of the ID for CCT nonprofits and ID for Propublica nonprofits.

matches_pp_ma.csv -
CSV file of the matches that record_linkage.py identifies between nonprofits that received funding from MacArthur foundation and Propublica nonprofits. The file has a column of the ID for MacArthur nonprofits and ID for Propublica nonprofits.

nonprofits.csv -
file of the scraped nonprofit information from Propublica. The columns are nonprofit name, address, IRS code, Active (defined as having filed IRS 990 form during or after 2015), latest yearCSV  (that the nonprofit filed an IRS 990 form), info year (the year the financial information that follows come from), revenue, expenses, assets, liabilities, revenue from contributions, revenue from program services.

propublica_scraper.py -
Scrapes the Propublica website starting from advanced search with state set to IL and city set to Chicago. Takes at least 4 hours to run because forced to make program sleep after each request to Propublica.

record_linkage.py -
Performs record linkage between Propublica and Chicago Community Trust, and Propublica and MacArthur Foundation.

mac_scrape.py -
Scrapes Macarthur Foundation’s website for organization name, amount of donation received, year, duration, and organization description in Chicago IL for 2016-2017

mac_grants+descriptions.csv -
Output csv from mac_scrape.py.

sql_queries_final.py -
Creates the output string to be printed on the django webform.

Geolocating.py -
Writes csv with propublica nonprofit information and gps coordinate information for each address. Takes several hours to run because geopy has a one query per second limit.

Coordinates2.csv -
Output csv from geolocating.py.

myform/form_app/models/(all contents) -
The machine learning models

myform/with_coords -
The database used during implementation.

No_coords_mod -
This file uses the tables built and populated in no_coords_build.py to perform record linkage from the matches csv’s. The final table it produces is mcp, which has an official name for the record, the data, a rowid, and IDs that link to the tables with all the information about each record.

No_coords_build -
Builds the SQL tables from csv files. Each table is populated at the sqlite3 command line.

cct_scraper.py -
Scrapes the Chicago Community Trust website for organizations and their grants for the past 10 years. Change offset= in the starting url to run a segment of the scraper.

all_pages_grants.csv -
Output csv from cct_scraper.py containing name of foundation, amount donated, year donated, reason for donation.

all_pages_orgs.csv -
Output csv from cct_scraper.py containing organization descriptions.

Zipcode_regex.py -
Function to parse zipcode from nonprofits.csv.

---

We have also submitted some deprecated code and files that show some of the avenues that we put significant work into exploring but that were ultimately not included in the final product.

add_weights.py -
used as part of an early framework for directly integrating the KMeans model outputs into the database.

graphing.py -
 used to test networkx algorithms

nlp_keywords.py -
used to create a tf-idf matrix of the top 1000 unigrams and 500 trigrams. This was replaced (at some loss of flexibility) by the built-in scikit vectorizers when we started using scikit clustering methods because of difficulties encountered transforming the .csv output of this file into a format scikit functions could use.

dtm.csv & cct_dtm.csv -
document term matrices created by early uses of nlp_keywords.py
