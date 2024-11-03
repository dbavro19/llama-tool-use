import requests
import streamlit as st
import pandas as pd
from misc_functions import call_llm, to_bool


#---------------------------This file contains the tool to call the MarketData API and retrieve real time stock information--------------------

#----------------------------- Documentation for the API available here https://www.marketdata.app/docs/api/stocks/quotes -------------------


# This Method will return the Stock Tool Spec so it can be added to the Tool Configuration
def get_stock_tool():
#Stock Price Tool
    get_stock_price = {
        "toolSpec": {
            "name": "get_stock_price",
            "description": "Gets real-time prices for a given company, stock, or instrument. Can also provide 52 week high and low price quotes for a stock. Returns MarketData api results",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "stock_symbol": {
                            "type": "string",
                            "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
                        },
                        "user_question":{
                            "type": "string",
                            "description": "The most recent question asked by the user question that prompted the tool - should be related to stock prices or stock details"

                        },
                        "get_52_week_details": {
                            "type": "boolean",
                            "description": "True if 52 week details are requested"
                        }
                    },
                    "required": ["stock_symbol", "user_question"]
                }
            }
        }
    }
    return get_stock_price






#Method to call the tool get_stock_price which retrieves stock infomration
def get_stock_price(stock_symbol, user_question, get_52_week_details, return_to_llm=False):

    st.write(f"Retrieving stock price for: {stock_symbol}")
    # Logic to retrieve stock price

    #Check if 52_week_details is a boolean, if not convert it to boolean

    if not isinstance(get_52_week_details, bool):
        get_52_week_details = to_bool(get_52_week_details)
    else:
    # Value is already a boolean, no conversion needed
        pass


    if get_52_week_details==True:
        api_url = f"https://api.marketdata.app/v1/stocks/quotes/{stock_symbol}/?52week=true"

    else:
        api_url = f"https://api.marketdata.app/v1/stocks/quotes/{stock_symbol}"

    st.write(f"Using {api_url} to retrieve stock data")

    response = requests.request("GET", api_url)


    results = response.text
    try:
        df = pd.read_json(results)
    except:
        df = results
    st.write("Raw Results from API:")
    st.write(df)

    #Set User Prompt
    user_prompt = f"""Based on the information provided by the tools, summarize or give me a final answer to my question
    Keep the answer accurate and concise

    my question: {str(user_question)}
    
    Information : {str(results)}

    """
    # Set System Prompt
    system_prompt = """
    You are a Financial Research AI assistant. Answer the user's question accurately and concisely based on the information provided
    """
    st.write("Sending Raw Results to LLM for Summarization")
    llm_response = call_llm(user_prompt, system_prompt)

    st.write(f"LLM Response: {llm_response}")

    return llm_response

