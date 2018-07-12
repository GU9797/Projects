#Edwin Gavis, Mike Gu, Mia Leatherman and Michelle Li 
#03-12-2018

import random

import collections
import geopy
import geopy.distance as gpd
import jellyfish
import math
import numpy as np
import pandas as pd
import sqlite3 as sql

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from sklearn.externals import joblib
from stemming.porter2 import stem

from .forms import FullEntryForm

def get_name(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FullEntryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            data = form.cleaned_data
            data['text'] = " ".join([data['keywords'], data['name'], data['description']])
            id_list = execute(data)
            connections = get_output_string(id_list)
            return HttpResponse('Okay, {}, here are some useful connections: <br/>{}.'.format(form.cleaned_data['name'], connections))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = FullEntryForm()

    return render(request, 'name.html', {'form': form})


##########################################

##GLOBAL CONTROL PANEL##
IRS_SCORE = 3
IRS_COLLAPSE = 1
OTHER_SCORE = 1

ML_SCORE = 1
ML_COLLAPSE = 0.25
 
SIZE_SCORE = 1
DIST_MAX = 1 
DIST_MULT = 2 #1/(log(d) * mult)
 
def execute(d):
    '''
    Takes the dictionary of user inputs (d) via django and returns 
    the masterID of the ten highest scored nonprofits.
    '''
    G = collections.defaultdict(int)
    name_code, txt_code, irs_code, combined_code = get_predictions(d)
    #print(combined_code) #debugging
    name_list = build_lists('km_name_model.pkl', 'km_name_misses.pkl')
    txt_list = build_lists('km_txt_model.pkl', 'km_txt_misses.pkl')
    irs_list = build_lists('km_irs_model.pkl', "km_irs_misses.pkl")
    combined_list = build_lists("km_combined_model.pkl")
    #print(combined_list) #debugging
    add_keyword_scores(G, d)
    print("keyworded " + str(len(G.keys())))
    name_l = gen_ml_links(name_code, name_list)
    txt_l = gen_ml_links(txt_code, txt_list) 
    irs_l = gen_ml_links(irs_code, irs_list)
    combined_l = gen_ml_links(combined_code, combined_list)
    ranked = rank_ml(name_l, txt_l, irs_l, combined_l)
    add_ml_scores(G, ranked)
    count = 0
    Gfinal = {}
    X = sorted(G, key = G.get, reverse = True)
    print("N Guesses: " + str(len(X)))
    for w in X:
        #print((w, G[w])) #DEBUGGING
        Gfinal[w] = G[w]
        count += 1
        if count >= 50: 
            break
    n_r_c_query = '''SELECT rowid, final_name, revenue, coords FROM mcp WHERE '''
    for i, org_code in enumerate(Gfinal):
        n_r_c_query += "rowid = " + str(org_code) + " OR "
    connect = sql.connect("with_coords")
    c = connect.cursor()
    n_r_c = c.execute(n_r_c_query[:-4]).fetchall()
    user_coords = get_user_location(d["zipcode"])
    revenue_dic = {
    "small": 22800,
    "medium": 112000,
    "large": 633000 
    } #FROM R CODEe
    org_names = set()
    for org in n_r_c:
        if org[1]:
            if jellyfish.jaro_winkler(
                                      d["name"].lower(), org[1].lower()
                                      ) >= 0.9 or org[1] in org_names:
                Gfinal[org[0]] = 0
                continue
            org_names.add(org[1])
        if d["size"] and org[2]:
            if int(org[2]) >= revenue_dic[d["size"]]:
                Gfinal[org[0]] += SIZE_SCORE
        if user_coords and org[3]:
            loc1 = (user_coords.latitude, user_coords.longitude)
            loc2 = org[3].strip("[]").split(", ")
            loc2 = [float(x) for x in loc2]
            dist = gpd.vincenty(loc1, loc2).miles
            if dist > 0:
                Gfinal[org[0]] += min(1 / 
                    (math.log(dist) * DIST_MULT), DIST_MAX)
            else:
                Gfinal[org[0]] += 1
    rv = []
    count = 0
    for org_code in sorted(Gfinal, key = Gfinal.get, reverse = True):
        print((org_code, Gfinal[org_code])) #DEBUGGING
        if org_code:
            rv.append(org_code)
        count += 1
        if count >= 10: 
            break
    return rv

def get_user_location(zipcode):
    '''
    Returns an object with attributes .longitude and .latitude corresponding
    to the coordinates of the given string (zipcode) or None if the string 
    cannot be located using Geopy's geocode function.
    '''
    geolocator = geopy.geocoders.Nominatim(timeout=4)
    rv = geolocator.geocode(zipcode)
    return rv


def rank_ml(name_l, txt_l, irs_l, combined_l):
    '''
    Sorts the KMeans models by the number of nonprofits they suggest,
    ascending.
    '''
    rv = []
    for l in [name_l, txt_l, irs_l, combined_l]:
        if l:
            rv.append(l)
    rv = sorted(rv, key=len)
    return rv

def add_ml_scores(G, ranked):
    '''
    Gives ML_SCORE points to each organization suggested by the KMeans 
    model with the fewest suggestions and a smaller number of points to 
    the suggestions of each subsequent KMeans model.
    '''
    score = ML_SCORE
    for ml_list in ranked:
        for val in ml_list:
            G[val] += score
        score -= ML_COLLAPSE

def get_predictions(d):
    '''
    Gets predictions from each KMeans model based on user input.
    '''
    name_code = predict_input(d['name'], 
        'km_name_model.pkl', 'km_name_vector.pkl')
    txt_code = predict_input(d['description'], 
        'km_txt_model.pkl', 'km_txt_vector.pkl')
    irs_code = predict_input(d['keywords'], 
        'km_irs_model.pkl', "km_irs_vector.pkl")
    combined_code = predict_input(d['text'], 
        "km_combined_model.pkl", "km_combined_vector.pkl")
    return name_code, txt_code, irs_code, combined_code

def predict_input(value, model, vector):
    '''
    Loads .pkl files of the model and its associated vectorizer 
    and uses them to make a prediction about (value).
    '''
    vec = joblib.load("form_app/models/"+vector) 
    clf = joblib.load("form_app/models/"+model)
    prediction = vec.transform([value])
    return clf.predict(prediction)

def gen_ml_links(code, cat_list):
    '''
    Returns the organizations that the model that produced 
    (cat_list) gave the same cluster number as the prediction 
    (code).
    '''
    rv = []
    for i, org in enumerate(cat_list):
        if org == code:
            rv.append(i)
    return rv

def add_keyword_scores(G, d):
    '''
    Checks for keywords in organization descriptions and gives 
    points if they are found.
    '''
    connect = sql.connect("with_coords")
    c = connect.cursor()
    org_text = c.execute('''SELECT final_name, text_dump, pp_text FROM mcp''').fetchall()
    keywords = d["keywords"].split(" ")
    for i, k in enumerate(org_text):
        other_org_text = "" 
        if k[0]:
            other_org_text += k[0] + " "
        if k[1]:
            other_org_text += k[1]
        current_score = IRS_SCORE
        for keyword in keywords:
            check_keyword = stem(keyword.lower())
            if k[2]:
                if check_keyword in k[2].lower():
                    G[i+1] += current_score
                    current_score -= IRS_COLLAPSE
                if other_org_text:
                    if check_keyword in other_org_text.lower():
                        G[i+1] += OTHER_SCORE

def build_lists(model, miss_l = None):
    '''
    Builds the lists of each KMeans model's classifications, 
    giving organizations without a score a 10 (=no classification).
    '''
    clf = joblib.load("form_app/models/"+model)
    if not miss_l:
        return list(clf.labels_)
    misses = set(joblib.load("form_app/models/"+miss_l))
    rv = []
    labels = list(clf.labels_)
    c = 0
    for i in range(0,9275):
        if i in misses:
            rv.append(10)
        else:
            rv.append(labels[c])
            c += 1
    return rv



############################################################

def get_ID_info(master_ID):
    '''
    Gets information of the nonprofit that has master_ID.
    '''

    connect = sql.connect("with_coords")
    c = connect.cursor()

    ids = c.execute('''SELECT ppID, cctID, maID, final_name FROM mcp
     WHERE rowid = ?;''', [master_ID]).fetchall()
    pp_id, cct_id, ma_id, final_name = ids[0]

    pp_info = []
    cct_org_info = []
    cct_money_info = []
    ma_info = []

    if pp_id:
        pp_info = c.execute('''SELECT * FROM pp_all WHERE rowid = ?'''
            , [pp_id]).fetchall()
    if cct_id:
        cct_org_info = c.execute('''SELECT description FROM cct_orgs_all 
            WHERE org_id = ?''', [cct_id]).fetchall()
        cct_money_info = c.execute('''SELECT funder, amount, grant_year, 
            purpose FROM cct_grants_all WHERE org_id = ?'''
            , [cct_id]).fetchall()
    if ma_id:
        ma_info = c.execute('''SELECT amount, grant_year, duration 
            FROM  mac_all WHERE rowid = ?''', [ma_id]).fetchall()

    return pp_info, cct_org_info, cct_money_info, ma_info, final_name


def get_all_info(master_IDs_list):
    '''
    Gets all information of the given master_ID nonprofits.
    '''
    pp_info_list = []
    cct_org_info_list = []
    cct_money_info_list = []
    ma_info_list = []
    final_name_list = []

    for master_ID in master_IDs_list:
        pp_info, cct_org_info, cct_money_info, ma_info, final_name \
        = get_ID_info(master_ID)
        pp_info_list.append(pp_info)
        cct_org_info_list.append(cct_org_info)
        cct_money_info_list.append(cct_money_info)
        ma_info_list.append(ma_info)
        final_name_list.append(final_name)        

    return pp_info_list, cct_org_info_list, cct_money_info_list, \
    ma_info_list, final_name_list


def check_nonempty(list_of_lists):
    '''
    Check if lists in list of lists empty.
    '''
    for a_list in list_of_lists:
        if a_list:
            return True
    return False


def get_output_string(master_IDs_list):
    '''
    Get string to be printed to screen.
    '''


    pp_info_list, cct_org_info_list, cct_money_info_list, ma_info_list,\
     final_name_list = get_all_info(master_IDs_list)

    final_string = ""

    for i in range(0, len(master_IDs_list)):    # For each nonprofit
        org_string = ""
        name = final_name_list[i]

        if pp_info_list[i]:   
            address = pp_info_list[i][0][1]
            irs_codes = pp_info_list[i][0][2]
            info_year = pp_info_list[i][0][5]
            revenue = pp_info_list[i][0][6]
            expense = pp_info_list[i][0][7]
            assets = pp_info_list[i][0][8]
            liabilities = pp_info_list[i][0][9]
            contributions_rev = pp_info_list[i][0][10]
            program_service_rev = pp_info_list[i][0][11]
            pp = "yes pp"
        else:
            pp = "no pp"

        if cct_org_info_list[i]:
            cct_description = cct_org_info_list[i][0][0]
        else:
            cct_description = []

        if cct_money_info_list[i]:
            cct_grants = cct_money_info_list[i]
            cct_funders = []
            cct_amount = []
            cct_year = []
            cct_purpose = []
            for grant in cct_grants:
                if grant:
                    cct_funders.append(grant[0])
                    cct_amount.append(grant[1])
                    cct_year.append(grant[2])
                    cct_purpose.append(grant[3])   
        else:
            cct_grants = []

        if ma_info_list[i]:
            ma_info = ma_info_list[i][0]
            if ma_info:
                ma_amount = ma_info[0]
                ma_year = ma_info[1]
                ma_duration = ma_info[2]
        else:
            ma_info = []

        org_string += ("<BR> <b>" + name.upper() + "</b> </BR>")

        if cct_description:
            org_string += ("<BR> <b> Description: </b> " + cct_description 
                + "</BR>")

        if pp == "yes pp":
            if irs_codes:
                org_string += ("<BR> <b> IRS Category: </b>" + irs_codes 
                    + "</BR>") 
            org_string += ("<BR> <b> Address: </b>" + address + "</BR>"
             + "<BR>" + "IRS Form 990 information for " 
             + str(info_year.strip(".0")) + "</BR>"
             + "<table> <tr> <th>Revenue</th> <th>Expenses</th>"
             + " <th>Assets</th> <th>Liabilities</th>  </tr>"
             + "<tr>   <td>$" + str(revenue) + "</td> <td>$" + str(expense)
             + "</td> <td>$" + str(assets)
             + "</td> <td>$" + str(liabilities) + "</td>  </tr>  </table>"
             + "Sources of Revenue: $" + str(contributions_rev) 
             + " from contributions, and $" + str(program_service_rev) 
             + " from program services" +"<BR> </BR>")

        if check_nonempty(cct_money_info_list[i]):
            org_string += "<BR> <b> Chicago Community Trust Funders </b> </BR>"
            for grant_num in range(0, len(cct_funders)):
                org_string += ("<BR>" + str(cct_funders[grant_num]) + " gave " 
                    + cct_amount[grant_num] + " in " + str(cct_year[grant_num])
                    + " for the given reason: " + str(cct_purpose[grant_num]) 
                    + "</BR>")
                
        if ma_info:
            org_string += ("<BR> <b> MacArthur Foundation </b> gave $" 
                + str(ma_amount) + " in "
                + str(ma_year) + " " + ma_duration + "</BR>")

        final_string += org_string + "<BR></BR>"

    if final_string == "":
        final_string = "No nonprofits found."

    return final_string

KEYWORDS = { 
"spiritual", 
"religion"
"sports",
"employment",
"professional"
"education",
"disaster",
"philanthropy",
"grantmaking",
"tech",
"science",
"arts",
"humanities",
"culture",
"support",
"foreign affairs",
"civil rights",
"community",
"medical",
"health",
"housing",
"research",
"college",
"nutrition",
"animal",
"benefit organization",
"mental health",
}