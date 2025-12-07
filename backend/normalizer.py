import pandas as pd
import numpy as np
import dateparser
import re
from thefuzz import process
from tabulate import tabulate
from backend import currency_conversion


# to identify merchants
MERCHANT_DF = pd.read_csv("databases/merchants.csv")
MERCHANT_LIST = MERCHANT_DF['merchant'].dropna().astype(str).str.upper().tolist()
MERCHANT_INDUSTRY = MERCHANT_DF.set_index(MERCHANT_DF['merchant'].astype(str).str.upper())['industry'].astype(str).str.upper().to_dict()

# to identify currencies
currency_df = pd.read_csv("databases/currencies.csv")
CURRENCY_SYMBOLS = {str(row["symbol"]): row["currency"] 
                    for _, row in currency_df.iterrows() if pd.notna(row["symbol"]) and row["symbol"] != ""}
# many currencies use the same symbol, in this case we are choosing these as the most common defaults but there are many duplicates
CURRENCY_SYMBOLS.update({
    "$": "USD",
    "€": "EUR",
    "£": "GBP"
})
KNOWN_CURRENCIES = set(currency_df["currency"].dropna().astype(str).str.upper())
ALL_SYMBOLS_REGEX = "[" + "".join(re.escape(s) for s in CURRENCY_SYMBOLS.keys()) + "]"


def is_date(value):
    if not isinstance(value, str):
        return False
    parsed = dateparser.parse(value, settings={'STRICT_PARSING': True})
    return parsed is not None

def is_currency(value):
    if not isinstance(value, str):
        return False
    value = value.strip().upper()
    return value in KNOWN_CURRENCIES

def is_amount(value):
    if not isinstance(value, str):
        return False
    v = value.strip()
    return bool(re.match(rf"^{ALL_SYMBOLS_REGEX}?\s*\d*([.,]\d+)?$", v))

def clean_date(value):
    return dateparser.parse(value)

def clean_amount(value):
    value_str = str(value).strip()
    match = re.search(r"[-+]?[0-9]*\.?[0-9]+", value_str.replace(",", ""))
    if match:
        return float(match.group())
    else:
        return None

def clean_merchant(value, threshold = 90):
    if not value or not isinstance(value, str):
        return None
    cleaned = value.replace("*", " ").replace("-", " ").replace("_", " ").strip()
    cleaned = " ".join(cleaned.split())
    cleaned = cleaned.upper()
    match, score = process.extractOne(cleaned, MERCHANT_LIST)
    # increase threshold to avoid normalizing name to wrong company
    if score >= threshold:
        return match
    else:
        return cleaned

# return a tuple (field_type, cleaned_value, extra_currency)
def detect_cell(cell):
    cell_str = str(cell).strip()

    # nothing passed in
    if not cell_str or cell_str == "nan":
        return ("invalid", "invalid", None)
    
    # if date
    if is_date(cell_str):
        return ("date", clean_date(cell_str), None)
    
    # if currency is a code (prioritize)
    if cell_str in KNOWN_CURRENCIES:
        return ("currency", cell_str, None)
    
    # if amount
    amount_match = re.match(rf"^(?P<symbol>{ALL_SYMBOLS_REGEX})?\s*(?P<number>\d*\.?\d+)?$", cell_str.replace(",", ""))
    if amount_match:
        symbol = amount_match.group("symbol")
        number = amount_match.group("number")
        # if currency symbol but no amount
        if symbol and not number:
            return ("amount", 0.0, CURRENCY_SYMBOLS.get(symbol))
        # if amount symbol or just amount
        if number:
            amount = float(number)
            currency = CURRENCY_SYMBOLS.get(symbol) if symbol else None
            return ("amount", amount, currency)

    # otherwise, merchant because merchant names are most ambiguous
    return ("merchant", cell_str, None)

def clean_dataframe(df):
    # new df
    rows = []

    for index, row in df.iterrows():

        # if row has all empty cells are passed in, skip processing row
        if all(pd.isna(cell) or str(cell).strip() == "" for cell in row):
            continue

        detected = {"date": None, "merchant": None, "normalized company name": None, "industry": None, "amount": None, "currency": None, "amount in USD": None}
        
        # detect each cell independently
        for cell in row:
            ftype, cleaned_value, extra_currency = detect_cell(cell)

            if ftype != "invalid":
                if ftype == "merchant" and cleaned_value is not None and not detected["merchant"]:
                    detected["merchant"] = cleaned_value
                    detected["normalized company name"] = clean_merchant(cleaned_value)
                elif detected[ftype] is None:
                    detected[ftype] = cleaned_value
        
                # only assign if that field is not already filled
                if detected[ftype] is None:
                    detected[ftype] = cleaned_value
                    
                # if extra currency from amount symbol, fill currency if empty
                if extra_currency:
                    detected["currency"] = extra_currency
        
        # add industry
        normalized_merch = detected["normalized company name"]
        if normalized_merch:
            detected["industry"] = MERCHANT_INDUSTRY.get(normalized_merch.upper(), "UNKNOWN")
        else:
            detected["industry"] = "UNKNOWN"
        
        # if no date detected in the row passed in
        if not detected["date"]:
            detected["date"] = "none"

        rows.append(detected)

    # create data frame of all cleaned rows
    clean_df = pd.DataFrame(rows)

    # if the currency missing in any row, fill it with the most common currency
    if not clean_df.empty and clean_df["currency"].isna().any():
        mode_values = clean_df["currency"].mode()
        if not mode_values.empty:
            common_currency = clean_df["currency"].mode()[0]
            clean_df["currency"] = clean_df["currency"].fillna(common_currency)

    # convert all amounts to USD and add to a new column
    if not clean_df.empty:
        amount_usd = []
        for i, row in clean_df.iterrows():
            if pd.notna(row["amount"]) and pd.notna(row["currency"]):
                converted = currency_conversion.convert_currency(row["currency"], "USD", row["amount"])
                amount_usd.append(converted)
            else:
                amount_usd.append(None)
        clean_df["amount in USD"] = amount_usd


    return clean_df

def print_file(input_path):
   print ("\n\nFirst few lines of the input file...")
   print ("--------------------------------------")
   n = 10  # number of lines you want
   with open(input_path, "r") as f:
       for i in range(n):
           line = f.readline()
           if not line:   # stop if the file is shorter than n lines
               break
           print(line, end="")
   print ("\n")
    
def normalize_csv(input_path):
   print ("\nProcessing input file: ", input_path)
 
   print_file(input_path)
   output_csv_path = "data/cleaned_data.csv"
   output_txt_path = "data/cleaned_data.txt"

    # if input csv is completely empty, return empty dataframe
   try:
       df = pd.read_csv(input_path, on_bad_lines="skip",  skipinitialspace=True)
   except:
       df = pd.DataFrame()

    # if csv file is only empty lines, create clenaed csv file with just the header
   if df.empty:
        columns = ["date", "merchant", "normalized company name", "industry",
                   "amount", "currency", "amount in USD"]
        clean_df = pd.DataFrame(columns=columns)
   else:
        clean_df = clean_dataframe(df)


   print ("First few lines of the cleaned file...")
   print ("--------------------------------------")
   print(clean_df.head(10))
   clean_df.to_csv(output_csv_path, index=False)
   with open(output_txt_path, "w") as f:
       f.write(tabulate(clean_df, headers="keys", tablefmt="pretty"))
   print ("\n")
   print(f"Cleaned file saved to {output_txt_path}")
   
