# Chicago Community Trust Scraper
# call with cct(ulr=myurl)

import bs4
import urllib3
import csv
import sqlite3


#change offset to run a segment; 120 runs all.
myurl = "http://cct.org/grants/?sort=organization_name&order=asc&offset=120"

pm = urllib3.PoolManager()
def cct(url):
    '''
    Crawls the CCT grants page and writes the data to a csv of all organizations
    and a csv of all grants.

    Inputs:
        url: starting url.
    '''
    all_organizations = []
    html = pm.urlopen("GET", url).data
    soup = bs4.BeautifulSoup(html, 'html5lib')
    tag_list = soup.find_all("td", class_="grantee")
    url_set = set()
    for tag in tag_list:
        url_set.update([tag.find("a", class_="org")['href']])
    for partial_url in url_set:
        all_organizations.append(each_page(partial_url))
    write_dic_to_db(all_organizations)
    write_org_to_id(all_organizations, "all_pages_orgs.csv", "all_pages_grants.csv")

def each_page(href):
    '''
    Crawls each link in main CCT page for our data.

    Input:
        href: partial url
    Returns:
        organization (dictionary) with title (string), description (string),
            grants (dictionary).
    '''

    # complete url
    full_url = "http://cct.org/what-we-offer/grants/" + href
    html = pm.urlopen("GET", full_url).data
    soup = bs4.BeautifulSoup(html, 'html5lib')
    # title
    header = soup.find("div", class_="cct-text-header")
    title = header.find("h1").text
    # description of org
    body = soup.find("div", class_="cct-text-main")
    t = body.find("p").next_sibling
    if type(t) == bs4.element.Tag:
        description = t.text.replace("\n", " ")
    else:
        description = None
    # grants
    grants = []
    grant_tag_list = soup.find_all("ul", class_="cct-grant-list")
    for grant in grant_tag_list:
        d = {}
        d["year"] = grant.find("span", class_="cct-grant-list__grant-year").text
        funder = grant.find("li", class_="cct-grant-list__grant cct-grant-list__grant--cat")
        d["funder"] = funder.find("a", class_="cct-grant-list__grant-funded-link").text
        amount = grant.find("li", class_="cct-grant-list__grant cct-grant-list__grant--amount")
        d["amount"] = amount.find("span", class_="cct-grant-list__grant-amount").text
        purpose = grant.find_next_sibling("p", class_="cct-grant-list__purpose").text
        purpose = purpose.strip() # remove spacing before
        purpose = purpose[8:] # remove "purpose"
        d["purpose"] = purpose.strip() # remove spacing after "purpose"
        grants.append(d)
    organization = {}
    organization["title"] = title
    organization["description"] = description
    organization["grants"] = grants
    return organization

def write_org_to_id(all_orgs, csvfile_orgs, csvfile_grants):
    '''
    Writes each organization and each of its grants to a csv.

    Inputs:
        all_orgs: list of dictionaries.
        csvfile_orgs: Organization csv
        csvfile_grants: Grants csv
    '''
    with open(csvfile_orgs, 'w', newline='') as csv_file1:
        writer = csv.writer(csv_file1)
        unique_ID = 0
        for dic in all_orgs:
            unique_ID += 1
            dic["id"] = unique_ID
            writer.writerow([dic["id"], dic["title"], dic["description"]])

    with open(csvfile_grants, 'w', newline='') as csv_file2:
        writer = csv.writer(csv_file2)
        for dic in all_orgs:
            for grant_d in dic["grants"]:
                writer.writerow([dic["id"], grant_d["funder"], grant_d["amount"], grant_d["year"], grant_d["purpose"]])
