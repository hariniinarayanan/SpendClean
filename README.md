# SpendClean
Smart financial parser and analyzer

SpendClean is a smart financial parser and analyzer designed to help users manage and analyze their financial data. It processes financial transactions, categorizes spending by industry, and provides insights into personal finance.

## Key Features
- **Automated Parsing**: Extracts relevant financial data from various messy formats.
- **Categorization**: Automatically categorizes expenses into predefined categories.
- **Data Analysis**: Provides insights and visualizations of spending habits.
- **Command-Line Interface**: Easy to use through CLI for quick access to functionalities.

### Installation
To install SpendClean, follow these steps:
1. Clone the repository
2. Navigate to the project directory (SpendClean)
3. Run the program using the command line
   ```
   ./run.sh
   ```
   This will process the data file located at `data/messy_data.csv`
4. To parse a specific input file of financial data, run using the command line
   ```
   ./run.sh {PATH_TO_INPUT_CSV}
   ```

### Directory Structure
The directory is structured as shown:
```
SpendClean/
├── backend/          # Backend processing files
├── cli/              # Command line interface files
├── data/             # Sample input and output data 
├── databases/        # Database files
├── .DS_Store
├── README.md         # Project documentation
└── requirements.txt  # Dependencies
```


## Program Methodology
This program handles messy financial data cleanly and effectively. It takes in a messy input file (csv) with four categories: **date, merchant, amount, and category**. 

*Note: A header line with these categories must be present in the input file for the function to work as intended.*

### Data Setup
I created a dummy CSV file named `messy_data.csv` to simulate common and uncommon inconsistencies found in financial datasets. The program handles several inconsisitencies in the dataset including:
- **Dates**: Various date formats such as `2023-01-05`, `Jan 5th 23`, `Jan 5th 23 12:01:45` and `01/05/2023`
- **Merchants**: Mixed naming conventions such as `UBER *TRIP`, `Uber Technologies`, and `UBER EATS`, misspelled company names such as `Strbucks`, inconsistent spacing (e.g. `  Walmart`)
- **Amounts/Currencies**: Varied currency symbols and spacing (e.g., `$20`, `20 USD`, and ` 15.50`), conflicting currencies such as `$20, EUR`, amounts with and without symbols, amounts with and without currencies, several currencies using the same symbol 
- **Missing/Invalid Values**: Rows with missing values (e.g. missing date), empty rows, unidentified merchant names, invalid dates such as `1-2-5`
- **Input File Inconsisitencies**: Rows with data in any order (e.g., `Jan 5th 23, 15, USD, Walmart`, `Walmart,,USD,15`), empty files 

### Data Ingestion and Normalization
For parsing, normalizing, and analyzing the dataset, I utilized the following tools:
- **Libraries Used**:
  * *OpenAI* : For conducting financial analysis of cleaned data.
  * *Pandas* : For data manipulation and cleaning.
  * *NumPy* : For numerical operations.
  * *TheFuzz* : To clean merchant names.
  * *Regular Expressions (`re`)* : For pattern matching symbols in data.
  * *CSV* : For reading and writing CSV files.
  * *Datetime* : For handling date and time data.
  
- **Databases**: 
  I accessed online databases to facilitate various operations:
  * *Currency Symbol to Code Conversion* : I used a database that maps currency symbols (like `$`, `€`, etc.) to their respective ISO 4217 currency codes (such as USD, EUR, etc.). This ensures that monetary amounts are uniformly recognized and processed in the analysis.
  * *Merchant to Industry Classification* : I used another database to provide a mapping of merchants to their respective industries. For example, identifying that transactions from "UBER" fall under the "Transportation" category. This classification helps in better understanding spending patterns.
- **APIs**: 
  I integrated APIs to enhance the project's functionality:
  * **OpenAI API** : This API was used for conducting complex financial analyses on the cleaned data. By prompting the API, I was able to generate insights, identify trends, and categorize expenses based on historical data patterns. **Requires an OpenAI API private key to successfully retrieve the spending analysis.**
  * **Currency Rate Conversion API** : I utilized an API to fetch _real-time currency conversion rates_. This allows the tool to convert amounts into a standard currency format, aiding in accurate financial reporting and analysis. For instance, if a transaction is in EUR, it can be converted to USD based on the latest exchange rates, ensuring a consistent dataset for analysis. Called using a free API key so all users can make calls.

### How the Ingestion and Normalization Functions Work:
1. **Load the data**: Using pandas, the messy data is ingested
2. **Iterate through rows**: Processes each row, identifying and cleaning each cell as a date, merchant, amount, or currency. Any cell can contain of the header values.
   * *Cleaning for each value:*
     - Date: standardize various date formats
     - Merchant Name: fix various spelling mistakes, inconsistent naming conventions, etc.
     - Amount: extract amount from inconsistent spacings, attached symbols, etc.
     - Currencies: convert symbols to currency, always prioritize/overwrite currency code (three letters) over symbol, extract currencies from amount column, fill missing values with the most common currency
3. **Create cleaned output CSV and txt file**: Adds cleaned row plus additional columns "cleaned company name" and "amount in USD" to new, cleaned dataset
   * *Calculating each value:*
     - Industry: use database to find corresponding industry of each merchant
     - Amount in USD: use API to convert each amount in its currency
4. **Aggregate cleaned data**: Analyze cleaned data to calculate which industry had the most spent and how much was spent in this industry.
5. **Perform AI analysis**: Perform an OpenAI call to conduct further analysis on financial spending patterns from the cleaned data.

### Analysis
The program outputs the first couple lines of the input file and the first couple lines of the output file. The output from the tool is a clean CSV file (`cleaned_data.csv`) and txt file (`cleaned_data.txt`) that consolidates all transactions into a standardized format. Once the data is cleaned, I also output a report that identifies the top spending category aggregation functions in Pandas. This helped provide insights from the financial data effectively. I also prompt OpenAI to output a more extensive financial analysis detailing total and average spending, top merchants by total spendings, unusual/irregular spending patterns, and more. Warning: OpenAI call requires a private API key or it will not run.

### Example Output
```
Processing input file:  /Users/harininarayanan/Downloads/messy_data.csv

First few lines of the input file...
--------------------------------------
date, merchant, amount, currency
2026/01/15,Costco,20.0,JPY
23/12/2025,BP,55.10,usd
2025.12.25,Valero,$65.75,USD
01/02/2023,UBER EATS,€8.50,EUR

First few lines of the cleaned file...
--------------------------------------
        date   merchant normalized company name     industry  amount currency  amount in USD
0 2026-01-15     Costco                  COSTCO       RETAIL   20.00      JPY        0.12886
1 2025-12-23         BP                      BP  GAS STATION   55.10      EUR       64.16395
2 2025-12-25     Valero                  VALERO  GAS STATION   65.75      USD       65.75000
3 2023-01-02  UBER EATS               UBER EATS     DELIVERY    8.50      EUR        9.89825

Cleaned file saved to data/cleaned_data.txt

*****************************************************
The industry with the highest spending is:  GAS STATION
Total spent in this industry is:            $ 129.91395
*****************************************************

Analyzing the spending patterns...
- **Total & average spending (sample data)**  
  - Total spent (USD-equivalent, using `amount in USD`): **$149.35**  
  - Number of transactions: **4**  
  - Average per transaction: **$37.34**
- **Top merchants by total spend**
  | Rank | Merchant  | Industry     | Total Spent (USD) | Number of Transactions |
  |------|-----------|-------------|-------------------|------------------------|
  | 1    | Valero    | GAS STATION | $65.75            | 1                      |
  | 2    | BP        | GAS STATION | $55.10            | 1                      |
  | 3    | Costco    | RETAIL      | $20.00            | 1                      |
  | 4    | UBER EATS | DELIVERY    | $8.50             | 1                      |
- **Unusual / irregular spending patterns (based on sample)**  
  - **Gas stations dominate**: ~81% of total spend is on gas (Valero + BP: $120.85 of $149.35). If this is atypical for you, it could indicate an unusually high period of driving or travel.  
  - **Single large transaction**: The **$65.75** charge at Valero is the largest single item (~44% of total spend), potentially noteworthy if gas fill-ups are usually smaller.  
  - **Sparse time coverage**: Only a few transactions spread across **2023–2026**, which suggests this is a partial data sample—insight on “irregular” behavior is limited without a fuller history. 
```

### Edge Cases Considered
- Empty input file
- File with only header
- File with empty lines
- Rows with one or more missing fields
- Rows with out of order fields
- Rows with duplicate fields (e.g., two columns with dates, two columns with conflicting currencies, etc.)
- Rows with 5+ columns (considered invalid entry)
- Rows with invalid field values

### Future Improvements
Given more time and access to wider resources, these are some improvements I would make:
* Provide a UI to
  - input CSV files
  - input individual lines of data
  - prompt user for missing data while analyzing rows
* Access real-time merchant database (from Visa, Mastercard, etc.) but that requires a subscription
* Use a local AI agent intead of making calls to OpenAI

### AI Tool Usage
I used AI to assist in:
* geneerating data parsing and normalizing skeleton code
* writing the regex for various tasks
* creating messy data CSV files
* retrieving spending analysis data
* debugging code



   

