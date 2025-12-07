import os
import pandas as pd
import numpy as np
import dateparser
import re
from thefuzz import process
from tabulate import tabulate
from backend import currency_conversion
from backend import normalizer

def aggregate_data(input_csv):
    
    input_data = pd.read_csv(input_csv)

    # if the input file is only the header, then skip processing
    if len(input_data) <= 1:
        print("\nCleaned Output File is Empty\n")
        return

    # group by "industry" columns
    industry_groups = input_data.groupby("industry")["amount in USD"].sum()
    most_spent_industry = industry_groups.idxmax()
    most_spent_amount = industry_groups.max()
    print ("\n*****************************************************")
    print("The industry with the highest spending is: ", most_spent_industry)
    print("Total spent in this industry is:            $", most_spent_amount)
    print ("*****************************************************\n")
 