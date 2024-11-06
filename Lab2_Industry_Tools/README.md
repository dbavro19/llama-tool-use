# AWS Bedrock Workshop - Lab 2

This lab introduces more complex tools and focuses on common industry workloads. While the implementation is simplified without extensive error handling, it demonstrates practical applications of LLM tools.

> Note: If you encounter any issues that can't be resolved in 10 minutes, you get a cup! 🏆

## Prerequisites Setup

### 1. SQLite Database Setup
We'll create a local SQLite database to simulate a trading order system.

> Note: While not covered in this lab, synthetic data generation is an excellent use case for LLMs (which was used to generate this data)

Change to the setup scripts directory:
```bash
cd Lab2_Industry_Tools/Lab_2_Setup_scripts
```

Run the SQL setup script:
```bash
python3 sql_setup.py
```

### 2. FAISS Vector Store Setup
Set up a local vector store with pre-loaded insurance documents:
```bash
python3 faiss_setup.py
```

### 3. S3 Bucket Configuration
1. Locate your S3 bucket name from the initial setup
2. Open `misc_functions.py` in the IDE
3. Find this code block (line 23) and replace the bucket_name value with your bucket name:

```python
###########################################################################################
### ----------LAB2 SETUP: Change this Method to add your bucket name here! ------------####
###########################################################################################
def get_bucket_name():
    bucket_name = "dome-test-meta-lab-12345" #Change this line to be YOUR bucket name that you created as part of the setup
    return bucket_name
```
4. Save the file

## Starting the Lab

Launch the Lab2 Frontend:
```bash
cd Lab2_Industry_Tools
```
```bash
streamlit run frontend_lab_2.py --server.port 8080 --server.enableXsrfProtection=False --server.enableCORS=False
```

## Available Tools

### 1. Calculator Tool
A fundamental tool for mathematical operations that converts natural language to mathematical expressions.

Example 1:
```plaintext
what is 38 minus 11
```

Example 2:
```plaintext
what is twenty two divided by 4 times 12 + the number of days in February on a leap year
```


To enable LLM response formatting, modify `tools_lab_2.py`:

Original code:
```python
if tool_name == 'calculator':
    results = calculator(**tool_parameters)
    results_type = "int"
    return_to_llm = False
```

Modified code:
```python
if tool_name == 'calculator':
    results = calculator(**tool_parameters)
    results_type = "int"
    return_to_llm = True
```

### 2. Industry-Specific Tools

#### A. Monte Carlo Simulator
Predicts asset volatility over time with visualizations.

Parameters:
- Initial value (required)
- Investment period (years)
- Number of simulations
- Annual return (%)
- Annual volatility (%)

Example:
```plaintext
Run a monte carlo simulation for $10,000 initial value over the course of a 5 year period with a return rate of 7% and a volatility rate of 12%
```

#### B. Stock Price Tool
Retrieves current stock prices and 52-week data (Limited to AAPL stock without API key).

Example 1:
```plaintext
What is apple trading at?
```

Example 2:
```plaintext
what is the 52 week high
```

Example 3:
```plaintext
Is apple up today?
```

Optional multi-tool example:
```plaintext
what is larger, 22*11 or the current apple stock price?
```
**Note: After testing with the multi-turn tool, revert the return_to_llm values for calculator tool and get_stock tool to False and refresh the page**


#### C. Insurance Policy FAQ Tool
RAG-based tool for insurance policy document queries.

Example 1:
```plaintext
How are settlements determined for covered losses (e.g. actual cash value, replacement cost)?
```

Example 2:
```plaintext
What vehicles are considered 'insured autos' under the policy?
```

#### D. Financial Article Analyzer
Extracts and analyzes financial articles with structured output.

Example 1:
```plaintext
Analyze this article - https://www.fool.com/investing/2024/10/21/5-reasons-to-buy-amazon-stock-like-theres-no-tomor/
```

Example 2:
```plaintext
analyze this article - https://ir.aboutamazon.com/news-release/news-release-details/2024/Amazon.com-Announces-Third-Quarter-Results/
```

#### E. Trade Confirmation Tool
Validates trade orders between email and database records.

Example 1:
```plaintext
Validate this trade - 
From Bob Smith
To: Trading Operations
Subject: Sell Order Request - US10Y Bonds - Trade_ID: 2

Hello Team,

Please enter a limit sell order for 200 units of 10 year US bonds with a target price of 98.50. This is for Portfolio PF_2, tagged under Account ACC_5678, with Trade_ID 2. Kindly execute by market close if the limit is hit; otherwise, keep it active until we decide on further action.

Let me know if there are any issues setting this up. I'll be available throughout the day if you need clarification.

Thanks,
Bob Smith
Fixed Income Trader
```

Example 2:
```plaintext
Validate this trade - 

From: Alice Johnson
To: Trade Desk
Subject: Trade Order Submission for Portfolio - Trade_ID: 1

Hello Trade Desk,
Please proceed with a market buy order for 200 shares of AAPL at the current market price. This trade is for Portfolio ID PF_1 for Account ACC_1235 and has been assigned Trade_ID: 1. I'd like it executed as soon as possible.
Thanks for confirming once it's filled. I'll be monitoring for updates.
Best,
Alice Johnson
Senior Trader - Equity Markets
```

#### F. Data Visualization Tool
Generates database visualizations from natural language queries.

Example 1:
```plaintext
Give me a bar chart showing Trade Volume by Asset Type
```

Example 2:
```plaintext
make a pie chart showing the quantity per each stock asset
```

Database Schema:
```sql
Trade_ID, Requested_By, Instrument_Type, Symbol_Ticker, Order_Type, Buy_Sell_Indicator, 
Quantity, Price, Requested_Urgency, Account_Number, Portfolio_ID TEXT, Trader_ID TEXT
```

Example Record:
```sql
(1, 'User_1', 'Stock', 'AAPL', 'Market', 'Buy', 100, 150.00, 'Immediate', 'ACC_1234', 'PF_1', 'TR_1')
```

#### G. Document Processing Tool
Processes various document types with confidence scoring:
- Auto Insurance Claim
- Drivers License
- Pay Stub
- W2 Form

Usage:
1. Upload document via sidebar
2. Submit processing request:
```plaintext
process this document
```

## Next Steps
The next section will cover creating custom tools from scratch with Llama's assistance.

