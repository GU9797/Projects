#############
#Find links between Propublica and MacArthur, Propublica and Chicago Community
#Trust.
#############

import re
import numpy as np
import pandas as pd
import jellyfish
import csv

# In anticiplation of SQL table, everything indexed from 1

def clean_df(df):
    '''
    Cleans the nonprofit names.
    '''
    df["nonprofit_name"] = df["nonprofit_name"].str.lower()
    df["nonprofit_name"] = df["nonprofit_name"].str.replace(r",|\.|\'|\-", "")
    df["nonprofit_name"] = df["nonprofit_name"].str.replace(r"\-", " ")
    return df


def get_all_df(pp_file, cct_file, ma_file):
    '''
    Get Propublica, Chicago Community Trust, and MacArthur csv file information
    into Pandas dataframes
    '''
    propublica_data = pd.read_table(pp_file, sep = '|',
        names = ["nonprofit_name", "address", "keywords", "active",
         "latest_year", "info_year", "revenue", "expense", "assets",
         "liabilities", "contributions_rev", "program_services_rev"])
    # Index from one
    propublica_data["index_num"] = (propublica_data.index + 1)
    cct_data = pd.read_csv(cct_file, names = ["index_num", "nonprofit_name",
     "description"])
    ma_data = pd.read_csv(ma_file, sep = "|", names = ["nonprofit_name",
     "funding", "year", "duration", "description"])
    ma_data["index_num"] = (ma_data.index + 1)    # Index from one

    propublica_data = clean_df(propublica_data)
    cct_data = clean_df(cct_data)
    ma_data = clean_df(ma_data)

    return propublica_data, cct_data, ma_data


def get_matches(pp_df, other_df):
    '''
    Get matches betweeh Propublica and other given (Chicago Community Trust or
     MacArthur). 0.9 jaro-winkler score set as threshold for match because 
     it works best at only letting in actual matches (although some matches
     fall just short but we prioritize minimizing false positives).

    Input:
        pp_df (pandas dataframe): propublica df
        other_df (pandas dataframe): other df

    Returns: dictionary of matches and unmatches
    '''

    matches_index_dict = {"pp_index": [], "other_index": []}
    unmatches_index_dict = {"pp_index": [], "other_index": []}

    for other_row in other_df.itertuples():
        highest_jw = -1
        best_match_pp_index = -1

        for pp_row in pp_df.itertuples():
            name_score = jellyfish.jaro_winkler(other_row.nonprofit_name,\
             pp_row.nonprofit_name)
            if name_score > highest_jw:
                highest_jw = name_score
                best_match_pp_index = pp_row.index_num

        if highest_jw > 0.9:      # Set at 0.9 because it worked best
            matches_index_dict["pp_index"].append(best_match_pp_index)
            matches_index_dict["other_index"].append(other_row.index_num)
        else:
            unmatches_index_dict["pp_index"].append(best_match_pp_index)
            unmatches_index_dict["other_index"].append(other_row.index_num)

    return matches_index_dict, unmatches_index_dict


def make_final_dataframe(index_dict, pp_df, other_df):
    '''
    Makes final dataframes of matches between propublica and other

    Inputs:
        index_dict (dictionary): of pp_index and cct_index that belong
            in the dataframe being constructed
        pp_df (Pandas DataFrame): dataframe of pp information
        other_df (Pandas DataFrame): dataframe of other information

    Output: Pandas DataFrame
    '''
    final_dataframe = pd.DataFrame(index_dict)
    final_dataframe = pd.merge(pp_df, final_dataframe, left_on = "index_num",
        right_on = "pp_index")
    final_dataframe = pd.merge(other_df, final_dataframe, 
        left_on = "index_num", right_on = "other_index", suffixes = ["_other",\
         "_pp"])
    final_dataframe = final_dataframe.drop(["nonprofit_name_pp", 
     "nonprofit_name_other", "address", "keywords", "active", "latest_year",
     "info_year", "revenue", "expense", "assets", "liabilities", 
     "contributions_rev", "program_services_rev",
     "description", "index_num_pp", "index_num_other"], axis = 1)
    return final_dataframe


def go(pp_file, cct_file, ma_file):
    '''
    Get matches csv files for Propublica and Chicago Community Trust, and
    Propublica and MacArthur. Left Column are either CCT or MA, right Column
    is Propublica index.
    '''
    pp_df, cct_df, ma_df = get_all_df(pp_file, cct_file, ma_file)

    pp_cct_matches_dict, pp_cct_unmatches_dict = get_matches(pp_df, cct_df)
    pp_ma_matches_dict, pp_ma_unmatches_dict = get_matches(pp_df, ma_df)

    pp_cct_matches = make_final_dataframe(pp_cct_matches_dict, pp_df, \
        cct_df)

    pp_ma_matches = make_final_dataframe(pp_ma_matches_dict, pp_df, ma_df)
    pp_ma_matches = pp_ma_matches.drop(["funding", "year", "duration"],
     axis = 1)

    pp_cct_matches.to_csv("matches_pp_cct.csv", sep=",", index = False,
     header = False)
    pp_ma_matches.to_csv("matches_pp_ma.csv", sep=",", index = False,
     header = False)







###############################################################################
##OLD CODE
###############################################################################

def get_complete_matches(pp_file, cct_file):

    known_links_dict = {"pp_name": [], "cct_name": []}
    propublica_df, cct_df = get_pp_cct_df(pp_file, cct_file)
    for pp_row in propublica_df.itertuples():
        for cct_row in cct_df.itertuples():
            if pp_row.nonprofit_name == cct_row.nonprofit_name:
    #            known_links_dict["pp_index"].append(pp_row.index_num)
     #           known_links_dict["cct_index"].append(cct_row.index_num)
                known_links_dict["pp_name"].append(pp_row.nonprofit_name)
                known_links_dict["cct_name"].append(cct_row.nonprofit_name)
   # known_links_dict["pp_index"].extend([3869, 4544, 3439, 9181, 4938, 7116,
   #  5843, 3214, 5189, 6098, 537, 5634, 8648, 1814, 1885, 5013, 4042, 10779,
    #  7214, 8027, 8067])
  #  known_links_dict["cct_index"].extend([123, 6, 26, 35, 38, 69, 71, 77, 81,
   #  128, 152, 190, 208, 218, 214, 217, 212, 266, 319, 358, 392])
    return known_links_dict


def get_known_pp_cct_links():
    '''
    Manually found matches. Ended up not using this way because it was taking
    too long to get all the manual matches and the way I was determining cut
    offs was letting in too many false positives.
    '''
    known_links_dict = {"pp_name": [], "cct_name": []}
    known_links_dict["pp_name"].extend(["matthew house",
     "the jackson chance foundation", "heartland human care services inc",
     "the vivian g harsh society inc harsh society", 
     "bella cuisine kids cooking club inc", "affinity community services",
     "inner voice incorporated", "audience architects nfp", "dance colective",
     "metropolis strategies nfp dba metropolis strategies",
     "the chicago lighthouse for people who are blind or visually impaired",
     "goodcity nfp", "night ministry", "roger baldwin foundation of aclu inc",
     "sit stay read inc", "casa central social services corporation", 
     "old town school of folk music inc", "mary arrchie theatre co",
     "apna ghar inc our home", 
     "golden apple foundation for excellence in teaching",
     "greater roselandwest pullman food network n f p"])

    known_links_dict["cct_name"].extend(["matthew house of chicago inc",
     "jackson chance foundation", "heartland human care services",
     "vivian g harsh society inc", "bella cuisine kids cooking club",
     "affinity community services inc", " inner voice inc", 
     "audience architects", "the dance colective", "metropolis strategies",
     "chicago lighthouse for people who are blind or visually impaired",
     "goodcity", "the night ministry", 
     "the roger baldwin foundation of aclu inc", "sit stay read", 
     "casa central", "old town school of folk music", "mary arrchie theatre",
     "apna ghar", "the golden apple foundation for excellence in teaching",
      "greater roselandwest pullman food network"])
    matches_dataframe = pd.DataFrame(known_links_dict)

    jw_scores = []
    for matches_row in matches_dataframe.itertuples():
        name_score = jellyfish.jaro_winkler(matches_row.cct_name,
         matches_row.pp_name)
        jw_scores.append(name_score)

    jw_series = pd.Series(jw_scores)
    matches_dataframe['jw'] = jw_series.values

    return matches_dataframe

def get_unmatches_cc_pp(pp_file, cct_file):
    '''
    Gets training unmatches
    '''

    pp_df, cct_df = get_pp_cct_df(pp_file, cct_file)
    # Random rows
    random_pp = pp_df.sample(1000, replace = True, random_state = 1234)\
    .reset_index(drop = True)
    random_cct = cct_df.sample(1000, replace = True, random_state = 5667)\
    .reset_index(drop = True)

    # Training unmatches df
    unmatches = pd.merge(random_pp, random_cct, left_index = True, 
        right_index = True, suffixes = ["_pp", "_cct"])

    unmatches = unmatches.drop(["index_num_pp", "index_num_cct", "address",
     "keywords", "active", "latest_year", "info_year", "revenue", "expense", 
     "assets", "liabilities", "contributions_rev", "program_services_rev", 
     "description"], axis = 1)

    jw_scores = []
    for unmatches_row in unmatches.itertuples():
        name_score = jellyfish.jaro_winkler(unmatches_row.nonprofit_name_cct,
         unmatches_row.nonprofit_name_pp)
        jw_scores.append(name_score)

    jw_series = pd.Series(jw_scores)
    unmatches['jw'] = jw_series.values

    return unmatches



def determine_jw_cut_offs(pp_file, cct_file):
    '''
    Meant to determine jw score cut off for matches, unmatches, and
    possible. Didn't work well because let in too many false positives.
    To be match, had to be greater than the highest jw score in the training
    unmatches. Anything below lowest jw score in training matches was an 
    unmatch. Anything in between these cut offs were just possible.
    '''
    matches_df = get_known_pp_cct_links()
    unmatches_df = get_unmatches_cc_pp(pp_file, cct_file)

    lowest_match_jw = min(matches_df['jw'])

    highest_unmatch_jw = max(unmatches_df['jw'])

    return lowest_match_jw, highest_unmatch_jw

def Xget_cct_pp_matches(pp_file, cct_file, ma_file, just_index = True):
    '''
    Abandoned for reasons stated above. Went with 0.9 jw score as cut off
    '''
    lowest_match_jw, highest_unmatch_jw = determine_jw_cut_offs(pp_file, cct_file)
    pp_df, cct_df, ma_df = get_pp_cct_df(pp_file, cct_file, ma_file)

    matches_index_dict = {"pp_index": [], "cct_index": []}
    unmatches_index_dict = {"pp_index": [], "cct_index": []}
    possible_index_dict = {"pp_index": [], "cct_index": []}


    for cct_row in cct_df.itertuples():
        highest_jw = -1
        best_match_pp_index = -1

        for pp_row in pp_df.itertuples():
            name_score = jellyfish.jaro_winkler(cct_row.nonprofit_name, 
                pp_row.nonprofit_name)
            if name_score > highest_jw:
                highest_jw = name_score
                best_match_pp_index = pp_row.index_num

        if highest_jw > highest_unmatch_jw:
            matches_index_dict["pp_index"].append(best_match_pp_index)
            matches_index_dict["cct_index"].append(cct_row.index_num)
        elif highest_jw < lowest_match_jw:
            unmatches_index_dict["pp_index"].append(best_match_pp_index)
            unmatches_index_dict["cct_index"].append(cct_row.index_num)
        else:
            possible_index_dict["pp_index"].append(best_match_pp_index)
            possible_index_dict["cct_index"].append(cct_row.index_num)

    if just_index:
        matches_df = pd.DataFrame(matches_index_dict)
        possible_df = pd.DataFrame(possible_index_dict)
        unmatches_df = pd.DataFrame(unmatches_index_dict)
        return matches_df, possible_df, unmatches_df

    matches_df = make_final_dataframe(matches_index_dict, pp_df, cct_df)
    possible_df = make_final_dataframe(possible_index_dict, pp_df, cct_df)
    unmatches_df = make_final_dataframe(unmatches_index_dict, pp_df, cct_df)
    return matches_df, possible_df, unmatches_df
