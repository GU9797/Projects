# Propublica scraper

import re
import bs4
import sys
import csv
import requests
import time


def get_names(soup):
    '''
    Crawls for names of the nonprofits in given ProPublica page soup
    of a search result page.

    Input:
        soup (BeautifulSoup soup): soup to look for name in

    Output: list of strings (names)
    '''
    potential_names = soup.find_all('td', class_='name')
    names_list = []

    for name_tag in potential_names:
        name = name_tag.find('a')
        name = name.text
        secondary_name = name_tag.find('span', class_="secondary-name")
        if secondary_name:
            secondary_name = secondary_name.text
            secondary_name = secondary_name[1:]
            name += secondary_name
        names_list.append(name)
    return names_list


def get_keywords(soup):
    '''
    Crawls for IRS keywords of the nonprofits in given ProPublica page soup
    of a search result page.

    Input:
        soup (BeautifulSoup soup): soup to look for keywords in

    Output: list of strings (keywords, if not exist, empty string)
    '''

    potential_keywords = soup.find_all('td', class_='ntee')
    words_list = []

    for words_tag in potential_keywords:
        primary_words_tag = words_tag.find('a')
        if primary_words_tag is None:   # If keyword not exist for org
            words_list.append("")
            continue
        primary_words = primary_words_tag.text
        secondary_words_tag = words_tag.find('span', class_="secondary-name")
        if secondary_words_tag:
            secondary_words = secondary_words_tag.contents[1].rstrip('\n  ')
        else:
            secondary_words = ""
        words = primary_words + secondary_words
        words_list.append(words.replace(',', ''))
    return words_list


def get_address(soup):
    '''
    Gets address of the nonprofit whose individual page's soup is inputted.

    Input:
        soup (BeautifulSoup soup): soup to look for address in

    Output: string (address)
    '''
    address_tag = soup.find('span', class_='small-label')
    if address_tag:
        address = address_tag.text.replace(',', '')
    else:
        address = ""
    return address


def get_irs_info(soup):
    '''
    Gets IRS 990 form information of the nonprofit whose individual page's
    soup is inputted.

    Input:
        soup (BeautifulSoup soup): soup to look for IRS info in

    Output: dictionary
    '''

    irs_info = {"active": False, "latest_year": None, "info_year": None,
     "revenue": None, "expense": None, "total_assets": None,
     "total_liabilities": None, "contributions_revenue": None,
      "program_services_revenue": None}    # Initialize

    irs_info["latest_year"] = int(soup.find_all('h4', class_= None)[1].text)

    if irs_info["latest_year"] >= 2015:
        irs_info["active"] = True

    # Want latest IRS info Propublica provides
    irs_info_tag = soup.find("table", class_="revenue monospace-numbers")

    if irs_info_tag:   # If such information exists
        revenue = irs_info_tag.find('th', class_="pos")
        if revenue:
            revenue = re.sub(r'[\$,]', '', revenue.text)
            irs_info["revenue"] = int(revenue)
        else:   # Tag class can be inconsistent
            revenue = irs_info_tag.find('th', class_="neg")
            if revenue:
                revenue = re.sub(r'[\$,]', '', revenue.text)
                irs_info["revenue"] = int(revenue)
        expense = irs_info_tag.find('th', class_="tablenum neg")
        if expense:
            expense = re.sub(r'[\$,]', '', expense.text)
            irs_info["expense"] = int(expense)

        assets_tag = irs_info_tag.find('td', class_ = "tablenum pos")
        a_tag_type = "pos"
        if not assets_tag:
            assets_tag = irs_info_tag.find('td', class_ = "tablenum neg")
            a_tag_type = "neg"
        total_assets = re.sub(r'[\$,]', '', assets_tag.text)
        irs_info["total_assets"] = int(total_assets)

        liabilities_tag = irs_info_tag.find_all('td', class_ = "tablenum neg")
        l_tag_type = "neg"
        if not liabilities_tag:
            liabilities_tag = irs_info_tag.find_all('td', \
                class_ = "tablenum pos")
            l_tag_type = "pos"

        if (len(liabilities_tag) > 1) and (l_tag_type == a_tag_type):
            liabilities_tag = liabilities_tag[1]
        else:
            liabilities_tag = liabilities_tag[0]

        total_liabilities = re.sub(r'[\$,]', '', liabilities_tag.text)
        irs_info["total_liabilities"] = int(total_liabilities)

        source = irs_info_tag.find_all('td', class_="tablenum")
        contributions_revenue = re.sub(r'[\$,]', '', source[0].text)
        irs_info["contributions_revenue"] = int(contributions_revenue)

        program_services_revenue = re.sub(r'[\$,]', '', source[1].text)
        irs_info["program_services_revenue"] = int(program_services_revenue)
        irs_info["info_year"] = int(irs_info_tag.parent.parent.find('h4',\
         class_=None).text)

    return irs_info


def get_nonprofit_urls(soup):
    '''
    From a search result page soup, gather the urls that leads to each
    nonprofits own page/ url.

    Inputs:
        soup (BeautifulSoup): soup of search result page with nonprofit links

    Outputs: list of strings (urls)
    '''
    parent_url = "https://projects.propublica.org"
    url_list = []
    nonprofits = soup.find_all('td', class_='name')
    for nonprofit_tag in nonprofits:
        nonprofit_url = nonprofit_tag.find('a')
        url = parent_url + nonprofit_url['href']
        url_list.append(url)
    return url_list


def index_to_csv(nonprofit_dictionary, csv_filename):
    with open(csv_filename, 'w', newline = '') as csv_file:
        writer = csv.writer(csv_file, delimiter = "|")
        for nonprofit in nonprofit_dictionary:
            writer.writerow([nonprofit,
            nonprofit_dictionary[nonprofit]["address"],
            nonprofit_dictionary[nonprofit]["keywords"],
            nonprofit_dictionary[nonprofit]["irs_info"]["active"],
            nonprofit_dictionary[nonprofit]["irs_info"]["latest_year"],
            nonprofit_dictionary[nonprofit]["irs_info"]["info_year"],
            nonprofit_dictionary[nonprofit]["irs_info"]["revenue"],
            nonprofit_dictionary[nonprofit]["irs_info"]["expense"],
            nonprofit_dictionary[nonprofit]["irs_info"]["total_assets"],
            nonprofit_dictionary[nonprofit]["irs_info"]["total_liabilities"],
            nonprofit_dictionary[nonprofit]["irs_info"]\
            ["contributions_revenue"],
            nonprofit_dictionary[nonprofit]["irs_info"]\
            ["program_services_revenue"]])


def crawl_propublica_page(starting_url):
    '''
    Crawl a propublica search result page for information.

    Inputs:
        starting_url: urk of the search result page to crawl

    Outputs: dictionary of information with keys as nonprofit names
    '''
    nonprofit_index = {}

    starting_request = requests.get(starting_url)
    starting_soup = bs4.BeautifulSoup(starting_request.text, 'html5lib')
    names_list = get_names(starting_soup)
    for name in names_list:
        nonprofit_index[name] = {"keywords": None, "address": None,\
         "irs_info": None}

    keywords_list = get_keywords(starting_soup)
    url_list = get_nonprofit_urls(starting_soup)
    address_list = []
    irs_info_list = []

    for nonprofit_url in url_list:   # For each nonprofit
        nonprofit_url_request = requests.get(nonprofit_url)
        soup = bs4.BeautifulSoup(nonprofit_url_request.text, 'html5lib')
        address_list.append(get_address(soup))
        irs_info = get_irs_info(soup)
        irs_info_list.append(irs_info)
        time.sleep(2)     # Propublica is catching my scraping

    index_num = 0

    for nonprofit in names_list:
        nonprofit_index[nonprofit]["keywords"] = keywords_list[index_num]
        nonprofit_index[nonprofit]["address"] = address_list[index_num]
        nonprofit_index[nonprofit]["irs_info"] = irs_info_list[index_num]
        index_num += 1

    return nonprofit_index


def crawl_propublica(num_pages_to_crawl):
    '''
    Starting from first page of advanced search result of nonprofits in city
    set at Chicago and state set at Illinois.

    Input:
        num_pages_to_crawl: pages to crawl. Should put in 111 here, because
        this particular search returns 110 pages of search result.

    Output: creates a CSV file for each page
    (safe guard in case propublica crashes)

    !!!! To get final file run in command !!!!!
    sed 1d nonprofits_*.csv > nonprofits.csv
    '''

    url_prefix = ("https://projects.propublica.org/nonprofits/search?"
        "adv_search=1&c_code%5Bid%5D=&city=Chicago&ntee%5Bid%5D=&page=")
    url_suffix = "&q_all=&q_any=&q_none=&q_phrase=&state%5Bid%5D=IL"
    pages_list = []

    page_num = 1
    while page_num < num_pages_to_crawl:      # Get all the search result pages
        page = url_prefix + str(page_num) + url_suffix
        pages_list.append(page)
        page_num += 1

    page_num = 1
    for page_url in pages_list:
        page_info = crawl_propublica_page(page_url)
        name_of_file = "nonprofits_" + str(page_num) + ".csv"
        index_to_csv(page_info, name_of_file)
        page_num += 1


















###############################################################################
###############################################################################
# OLD CODE
def Xcrawl_propublica(num_pages_to_crawl):
    '''
    Had to abandon because Propublica kept crashing in middle of scraping.
    This function can only work if change input of crawl_propublica_page to
    soup.
    '''

    parent_url = "https://projects.propublica.org"

    starting_url = ("https://projects.propublica.org/nonprofits/search?"
        "adv_search=1&c_code%5Bid%5D=&city=Chicago&ntee%5Bid%5D=&page=1&q_all"
        "=&q_any=&q_none=&q_phrase=&state%5Bid%5D=IL")

    starting_request = requests.get(starting_url)
    starting_soup = bs4.BeautifulSoup(starting_request.text, 'html5lib')
    starting_info = crawl_propublica_page(starting_soup)
    propublica_info_dict = starting_info

    num_crawled = 1
    while starting_soup.find('span', class_="next") \
    and num_crawled < num_pages_to_crawl:
        next_page_tag = starting_soup.find('span', class_="next")
        next_page_url = parent_url + next_page_tag.find('a')['href']
        next_page_request = requests.get(next_page_url)
        next_page_soup = bs4.BeautifulSoup(next_page_request.text, 'html5lib')

        next_page_info = crawl_propublica_page(next_page_soup)   # SOUP WAS INPUT BEFORE
        propublica_info_dict.update(next_page_info)

        starting_soup = next_page_soup   # Update
        num_crawled += 1

    index_to_csv(propublica_info_dict, "nonprofits.csv")
