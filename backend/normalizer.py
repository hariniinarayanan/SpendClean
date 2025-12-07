import pandas as pd
import numpy as np
import dateparser
import re
from thefuzz import process


# to identify merchants
MERCHANT_DF = pd.read_csv("/Users/harininarayanan/Documents/Projects/SpendClean/databases/merchants.csv")
MERCHANT_LIST = MERCHANT_DF['merchant'].dropna().astype(str).str.upper().tolist()
MERCHANT_INDUSTRY = MERCHANT_DF.set_index(MERCHANT_DF['merchant'].astype(str).str.upper())['industry'].astype(str).str.upper().to_dict()

# to identify currencies
CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}
KNOWN_CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD", "INR", "JPY"]

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
    return bool(re.match(r"^[£€$]?\s*\d+([.,]\d+)?$", v))

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
    amount_match = re.match(r"^(?P<symbol>[£€$])?\s*(?P<number>\d*\.?\d+)?$", cell_str.replace(",", ""))

    if amount_match:
        symbol = amount_match.group("symbol")
        number = amount_match.group("number")
        # if currency symbol but no amount
        if symbol and not number:
            return ("amount", 0.0, CURRENCY_SYMBOLS.get(symbol))
        # if amount
        if number:
            amount = float(number)
            currency = CURRENCY_SYMBOLS.get(symbol) if symbol else None
            return ("amount", amount, currency)

    return ("merchant", cell_str, None)

def clean_dataframe(df):
    # new df
    rows = []

    for index, row in df.iterrows():
        detected = {"date": None, "merchant": None, "normalized company name": None, "industry": None, "amount": None, "currency": None}
        
        # detect each cell independently
        for cell in row:
            ftype, cleaned_value, extra_currency = detect_cell(cell)

            if ftype != "invalid":
                if ftype == "merchant" and cleaned_value is not None:
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
                    
        normalized_merch = detected["normalized company name"]
        if normalized_merch:
            detected["industry"] = MERCHANT_INDUSTRY.get(normalized_merch.upper(), "UNKNOWN")
        else:
            detected["industry"] = "UNKNOWN"
        
        rows.append(detected)

    clean_df = pd.DataFrame(rows)

    # if currency missing, fill most common
    if clean_df["currency"].isna().any():
        common_currency = clean_df["currency"].mode()[0]
        clean_df["currency"] = clean_df["currency"].fillna(common_currency)

    return clean_df

def normalize_csv(input_path):
    print ("\n===================================================")
    print ("processing input file: ", input_path)
    print ("===================================================")
    output_path = "data/cleaned_data.csv"
    df = pd.read_csv(input_path, header=0, on_bad_lines="skip",  skipinitialspace=True)
    clean_df = clean_dataframe(df)
    clean_df.to_csv(output_path, index=False)
    print ("\n\nFirst few lines of the cleaned file...")
    print ("--------------------------------------")
    print(clean_df.head(15))
    print ("\n")
    print ("===================================================")
    print(f"Cleaned file saved to {output_path}")
    print ("===================================================")
