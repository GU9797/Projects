import re
import pandas as pd
import csv
import itertools

def get_zip(address):
    '''
    Inputs: address (string)

    Returns: 5-digit zipcode (string)
    '''
    if address:
        exp = re.compile('(?<=CHICAGO IL )([0-9]{5})')
        if exp.search(address):
            return exp.search(address).group()
        else:
            return " "
    else:
        return " "