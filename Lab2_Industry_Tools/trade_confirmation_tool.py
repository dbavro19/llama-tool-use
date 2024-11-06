


import json
import os
import pandas as pd
import sqlite3
import re
import streamlit as st
from misc_functions import call_llm, parse_xml


# ----------------------------------This Tool compares Emails about Financial Trades with the records in a trading system and checks for consistency ----------------------------------
# ------------------- This Tool Needs some setup. In Lab_2_Setup_scripts, run python .\sql_setup .py - This setups the SQL database that will act as our trading system ---------------------


def get_trade_confirmation():
    trade_confirmation = {
        "toolSpec": {
            "name": "trade_confirmation",
            "description": "Validates a trading email against the user's trading system and checks for validity and consistency",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "trade_id": {
                            "type": "string",
                            "description": "The identified trade_id value from the email - usually a number"
                        },
                        "email_contents":{
                            "type": "string",
                            "description": "The full contents of the provided email to be validated"
                        }
                    },
                    "required": ["trade_id", "email_contents"]
                }
            }
        }
    }
    return trade_confirmation



def trade_confirmation(trade_id, email_contents, return_to_llm=False):
    st.write("Trade ID: ", trade_id)
    df = get_trade_info_sql(trade_id)
    st.write(df)

    example_format= """

<output_format>
[
    {
        "trade_id": "(Trade_ID)",
        "matching_status": "(Good/Bad/Trade Info Not Found)",
        "discrepancies": [],
        "trade_info": {
            "Trade_ID": "(Trade_ID)",
            "Instrument_Type": "(Stock/Bond)",
            "Symbol_Ticket": "(TickerSymbol)",
            "Order_Type": "(Market/Limit/Stop)",
            "Buy_Sell_indicator": "(Buy/Sell)",
            "Price": "(Price)",
            "Quantity": "(Quantity)",
            "Requested_Urgency": "(Immediate/EOD/Next Open/ Next Close)",
            "Account_Number": "(Account_Number)",
            "Portfolio_ID": "(Portfolio_ID)"
        },
        "email_info": {
           "Trade_ID": "(Trade_ID)",
            "Instrument_Type": "(Stock/Bond)",
            "Symbol_Ticket": "(TickerSymbol)",
            "Order_Type": "(Market/Limit/Stop)",
            "Buy_Sell_indicator": "(Buy/Sell)",
            "Price": "(Price)",
            "Quantity": "(Quantity)",
            "Requested_Urgency": "(Immediate/EOD/Next Open/ Next Close)".
            "Account_Number": "(Account_Number)",
            "Portfolio_ID": "(Portfolio_ID)"
        }
    }
]
</output_format>

"""

    
    #Set System Prompt
    system_prompt=f"""
You are an AI Financial Market Trading Assistant 
You will be provided with a trading email from a Portfolio Manager and the corresponding trade information from the trading system
Your task is to validate the email against the trade information and check for consistency

To do so you will do the following:
1. Extract the relevant information from the email - any fields that cant be determined from the email can be left as "UNDETERMINED" Values which can be ignored during comparison
2. Compare the extracted information with the trade information from the trading system
3. If there are discrepancies or differences between the two (not including "UNDETERMINED" values) the return a matching status of "Bad", otherwise if there are no discrepancies, return "Good"
4. Describe the discrepancies in a clear and concise manner
5. Create a json list that will return 3 objects - the full trade information, the extracted information from the email in the same format, and the matching status and discrepancies


Other Notes:
- Ticker Symbol values may vary in format from the email to the trading system. Email might use the company name or long form name, while the trading system will have it in the Ticker Symbol format
- ie. Apple and APPL or 30 Year US Bond and US30Y should be considered a good match


Here is the trade information from the trading system for the focus trade:
<original_trade_id>

{df}

</original_trade_id>


Example output:
<output_format>

{example_format}

</output_format>


</output_format>

Return the following in your response
Your full thought process in <thinking> xml tags
The json array of results in <json_results> xml tags - paying extra attention to creating valid and accurate json

"""
        

    #Set User Prompt
    user_prompt=f"""
    Email contents for Trade_ID {trade_id}:


    <trade_email>
    {email_contents}
    </trade_email>
    """

    results = call_llm(system_prompt, user_prompt, model_id="us.meta.llama3-2-90b-instruct-v1:0")

    thinking = parse_xml(results, "thinking")
    json_results = parse_xml(results, "json_results")

    print(f"Thinking: {thinking}")



    return_type = check_json(json_results)
    if return_type == False:
        return_type = "text"
    else:
        json_results = json.loads(json_results)
        
        # Extract the matching status
        matching_status = json_results[0]['matching_status'].lower()

        # Display result based on matching status
        if matching_status == 'good':
            st.success("😊 Trade Confirmation Successful!")
        elif matching_status == 'bad':
            st.warning("Trade Not Matching", icon="🚨")
        else:
            st.info(f"Matching status: {matching_status}")

        return_type = "json"

    print(f"Json_Results: {json_results}")




    return json_results, return_type


def check_json(data):
    if isinstance(data, dict):
        return True
    elif isinstance(data, str):
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False
    else:
        return False


    

def get_trade_info_sql(trade_id):
    # Extract numeric value from trade_id if it's a string
    if isinstance(trade_id, str):
        # Try to extract a number from strings like "TR_(x)"
        match = re.search(r'\d+', trade_id)
        if match:
            trade_id = int(match.group())
        else:
            # If no numeric part found, try to convert the whole string to int
            try:
                trade_id = int(trade_id)
            except ValueError:
                print(f"Invalid trade_id format: {trade_id}")
                return None
    elif not isinstance(trade_id, int):
        try:
            trade_id = int(trade_id)
        except (ValueError, TypeError):
            print(f"Invalid trade_id format: {trade_id}")
            return None

    db_file = 'test_database.db'  # Adjust this path if needed

    # Connect to the SQLite database file
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Retrieve the column names
    cursor.execute("PRAGMA table_info(trade_blotter)")
    columns = [col[1] for col in cursor.fetchall()]

    # Retrieve data for the specified Trade_ID
    cursor.execute("SELECT * FROM trade_blotter WHERE Trade_ID = ?", (trade_id,))
    row = cursor.fetchone()

    # Close the database connection
    connection.close()

    # Check if a record was found
    if row is None:
        print(f"No data found for Trade_ID {trade_id}")
        return None

    # Create a DataFrame with the column names and data
    df = pd.DataFrame([row], columns=columns)

    # Save to CSV
    print("Trade Information from DB:")
    print(df)

    return df
    
