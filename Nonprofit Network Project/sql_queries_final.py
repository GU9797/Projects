import sqlite3
import pandas as pd

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
