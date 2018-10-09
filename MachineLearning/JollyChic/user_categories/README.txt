This directory contains files for dividing the JollyChic user base into categories with the intention of creating new targeting opportunities.

UserDiscountBuckets.pdf
Separates users based on discount amount over order amount ratio given their entire order history.

Top10productscategory.pdf
Ranks the top 10 products and product categories for all users and users that have purchased those products (pay_status=1)

data_selection.sql
SQL Code for creating tables necessary for this analysis

10k.csv
Data from zybiro.bi_gu_user_cat_vec (see SQL Code), which gives the amount of products purchased for each user across 10 different product categories:
womensclothing, womensaccesories, beauty, kids, womensbags, womensshoes, cellphonesdigital, mensclothing, decor, other

kmeans.py
Separates data1.csv into 6 user clusters using k means clustering.

wholedataset_cat_feature_correlation.png
Seaborn feature correlation chart showing correlation between the 10 different product categories

cluster_csvs
Directory containing 6 resulting user clusters outputted from kmeans.py

cluster_analysis.py
For each cluster csv, denormalizes, calculates avg number of orders for each product category, and creates dataframe containing percentage of products in each product category for each cluster.

cluster_info.txt
Results from cluster_analysis.py and cluster centers
