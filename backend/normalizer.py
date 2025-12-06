import pandas as pd
import numpy as np
import dateparser
import re

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
    # print(dateparser.parse(value))
    return dateparser.parse(value)

def clean_amount(value):
    value_str = str(value).strip()
    match = re.search(r"[-+]?[0-9]*\.?[0-9]+", value_str.replace(",", ""))
    if match:
        return float(match.group())
    else:
        return None

def clean_merchant(value):
    if not value or not isinstance(value, str):
        return None
    cleaned = value.replace("*", " ").replace("-", " ").replace("_", " ").strip()
    cleaned = " ".join(cleaned.split())
    cleaned = cleaned.upper()
    return cleaned

# return a tuple (field_type, cleaned_value, extra_currency)
def detect_cell(cell):
    cell_str = str(cell).strip()

    # if date
    if is_date(cell_str):
        return ("date", clean_date(cell_str), None)
    
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

    # if currency
    curr_cell = cell_str.upper()
    if curr_cell in KNOWN_CURRENCIES or curr_cell in CURRENCY_SYMBOLS:
        if (curr_cell in CURRENCY_SYMBOLS):
            curr_cell = CURRENCY_SYMBOLS.get(curr_cell)
        return ("currency", curr_cell, None)

    # check for merchant name last because they could be any string and 
    # currency string can be mistaken for merchant name
    return ("merchant", clean_merchant(cell_str), None)

def clean_dataframe(df):
    # new df
    rows = []

    for index, row in df.iterrows():
        detected = {"date": None, "merchant": None, "amount": None, "currency": None}
        
        # detect each cell independently
        for cell in row:
            ftype, cleaned_value, extra_currency = detect_cell(cell)
    
            # only assign if that field is not already filled
            if detected[ftype] is None:
                detected[ftype] = cleaned_value
                
            # if extra currency from amount symbol, fill currency if empty
            if extra_currency and detected["currency"] is None:
                detected["currency"] = extra_currency
        
        rows.append(detected)

    clean_df = pd.DataFrame(rows)

    # if currency missing, fill most common
    if clean_df["currency"].isna().any():
        common_currency = clean_df["currency"].mode()[0]
        clean_df["currency"] = clean_df["currency"].fillna(common_currency)

    return clean_df

def normalize_csv(input_path="/Users/harininarayanan/Documents/Projects/smart-financial-parser/data/messy_data.csv", 
                  output_path="/Users/harininarayanan/Documents/Projects/smart-financial-parser/data/cleaned_data.csv"):
    df = pd.read_csv(input_path)
    clean_df = clean_dataframe(df)
    clean_df.to_csv(output_path, index=False)
    print(f"Cleaned file saved to {output_path}")
