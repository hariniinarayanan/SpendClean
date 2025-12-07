import os
import pandas as pd
from openai import OpenAI

def generate_spending_report(csv_file: str, max_rows: int = 200, model: str = "gpt-5.1") -> str:
   
    # load csv
    df = pd.read_csv(csv_file, parse_dates=["date"])

    # limit size of what's sent to AI to avoid cost
    csv_sample = df.head(max_rows).to_csv(index=False)

    # read API key from env variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Environment variable OPENAI_API_KEY is not set. Unable to get spending analysis report.")

    client = OpenAI(api_key=api_key)

    # build prompt for AI
    prompt = f"""
You are a financial analysis assistant.

The CSV contains spending data with columns:
date, currency, merchant, amount spent.

Please generate insights including:
- total and average spending
- list top merchants and amounts in a table format
- unusual or irregular spending

CSV sample:
{csv_sample}

"Give concise answer in few bullet points."
"""
    print("\nAnalyzing the spending patterns...\n")

    # call open AI API
    response = client.responses.create(
        model=model,
        input=prompt,
    )
    # printing response will give information about cost of API call
    # print("Response: ", response)
    
    # print open AI response
    report = response.output_text
    # optional: print immediately
    print(report, "\n")  
    return report
