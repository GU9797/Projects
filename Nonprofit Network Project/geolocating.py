import geopy.geocoders as gp
from geopy.distance import vincenty
from geopy.exc import GeocoderTimedOut
import pandas as pd
import numpy as np
import csv
import time
import re

'''
Creates a new csv containing information from nonprofits.csv and the 
the coordinates for the address of each active organization in nonprofits.csv
'''
geolocator = gp.Nominatim(timeout=4)
'''
Making default location Berkeley for addresses which do 
not run with geopy, such that the ambiguity about their
distance will not affect their weighting.
'''
location = geolocator.geocode("110 Sproul Hall, Berkeley CA, 94720")

with open('nonprofits.csv','r') as csvinput:
    with open('output2.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, delimiter = "|")
        reader = csv.reader(csvinput, delimiter = "|")
        reader = csvinput.readlines()
        k = 0
        for row in reader[k:]:
            row = row.split("|")
            if row[3] == "True":
                time.sleep(1.8) 
                #geopy only accepts one query per couple seconds
                address = row[1]
                street = re.compile("\d+\s\w+\s\w+\s\w+") 
                #using regex to parse street and zipcode
                zip_code = re.compile("\d{5}\W\d{4}") 
                try:
                	st = street.search(address).group()
                except:
                	street = re.compile("\d+\s\w+\s\w+")
                try:
                	st = street.search(address).group()
                except:
                	street = "None"
                try:
                	zc = zip_code.search(address).group()[:-5]
                except:
                	zc = "None"
                address_string = st + ", CHICAGO IL, " + zc
                if st == "None" or zc == "None":
                	address_string = "110 Sproul Hall, Berkeley CA, 94720"
                loc = geolocator.geocode(address_string)
                try:
                	row.append([loc.latitude, loc.longitude])
                except:
                	row.append([location.latitude, location.longitude])
                print(row)
                writer.writerow(row)
            k += 1    

'''
Concatenates two csv files created from running above code (due to timeout errors).
Removes index from csv and includes inactive organizations with a default coordinate 
location of Berkeley
'''
col_names = col_names2 + ["coordinates"]
col_names2 = ["name", "address", "desc", "active","latest","info_year","revenue", "expense", "assets", "liabilites","cont_rev", "other_rev"]

a = pd.read_csv("output.csv", delimiter= "|", names=col_names)
a["other_rev"] = a["other_rev"].str.strip()

b = pd.read_csv("output2.csv", delimiter= "|", names=col_names)
b["other_rev"] = b["other_rev"].str.strip()

ab = pd.concat([a,b], names=col_names)

nonprofits = pd.read_csv("nonprofits.csv", delimiter= "|", names=col_names2)
ab.index = list(range(ab.shape[0]))
nonprofits["coordinates"] = "[37.8687886, -122.2592009]"
k = 0
n = 1
for index, row in nonprofits.iterrows():
    if row["active"] == True:
        gps = ab.loc[n, "coordinates"]
        if type(gps) == pd.core.series.Series:
            gps = list(x)[0]
        nonprofits.loc[k, "coordinates"] = ''.join(x)
        n += 1
    k += 1
    if n == ab.shape[0]:
        break

nonprofits.to_csv("coordinates2.csv", sep="|", index=False, index_label=False)
