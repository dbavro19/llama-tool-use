import json
import random
import re
import sys
import inspect
import requests
import boto3
import botocore
import streamlit as st
from misc_functions import clean_and_convert_to_int, format_user_messages
#Adding in our tools that we separated out into files (for organizational purposes)

from stock_tool import get_stock_tool, get_stock_price 
from trivia_tool import get_basic_trivia_tool, basic_trivia_tool
from extract_financial_article_tool import extract_financial_article, get_extract_financial_article
from trade_confirmation_tool import get_trade_confirmation, trade_confirmation
from data_visualization_tool import get_data_visualization, data_visualization_tool
from insurance_account_q_and_a_tool import get_insurance_policy_frequently_asked_questions, insurance_policy_frequently_asked_questions
from monte_carlo_tool import get_monte_carlo, monte_carlo_simulator
from document_processing_tool import get_intelligent_document_processor, intelligent_document_processor
from math_tool import get_math_tool, calculator

#Variable that will hold our Tool Configuration - Predefining our Tools for Lab 1
tool_definition = []

tool_definition.append(get_basic_trivia_tool())
tool_definition.append(get_math_tool())
tool_definition.append(get_monte_carlo())
tool_definition.append(get_stock_tool())
tool_definition.append(get_insurance_policy_frequently_asked_questions())
tool_definition.append(get_extract_financial_article())
tool_definition.append(get_trade_confirmation())
tool_definition.append(get_data_visualization())
tool_definition.append(get_intelligent_document_processor())







    
#-------------How we call our tools ---------------------

def execute_tool(tool_name, tool_parameters):



    if tool_name == 'basic_trivia_tool':
        results = basic_trivia_tool(**tool_parameters)
        results_type = type(results)
        return_to_llm = False ##Adjust This to TRUE - return this to false after playing with multi-turn tool use


    elif tool_name == 'calculator':
        results = calculator(**tool_parameters)
        results_type = "int"
        return_to_llm = False 


    elif tool_name == 'monte_carlo_simulator':
        results = monte_carlo_simulator(**tool_parameters)
        results_type = "plotly"
        return_to_llm = False

    elif tool_name == 'get_stock_price':
        results = get_stock_price(**tool_parameters)
        results_type = type(results)
        return_to_llm = True # Adjust this to False after testing multi-turn tool use

    elif tool_name == 'insurance_policy_frequently_asked_questions':
        results = insurance_policy_frequently_asked_questions(**tool_parameters)
        results_type = "text"
        return_to_llm = False

    elif tool_name == 'extract_financial_article':
        results, results_type = extract_financial_article(**tool_parameters)
        return_to_llm = False

    elif tool_name == 'trade_confirmation':
        results, results_type = trade_confirmation(**tool_parameters)
        return_to_llm = False

    elif tool_name == 'data_visualization_tool':
        results, results_type = data_visualization_tool(**tool_parameters)
        return_to_llm = False


    elif tool_name == 'intelligent_document_processor':
        if 'url' in tool_parameters:
            print("IT DID THE THING WITH THE WRONG PARAM NAME")
            tool_parameters = tool_parameters.replace("url=", "file")
            if 'file' in tool_parameters:
                    tool_parameters = tool_parameters.replace("web_", "")

        results = intelligent_document_processor(**tool_parameters)
        results_type = "json"
        return_to_llm = False

    else:
        results = "Tool Not Found"
        results_type = "text"
        return_to_llm = False

    

    
    
    return results, results_type, return_to_llm
    







def get_tools():
    return tool_definition

def get_tools_pretty():
    # Parse tool name and tool definitions
    tool_json = get_tools()
    return [{tool['toolSpec']['name']: tool['toolSpec']['description']} for tool in tool_json]