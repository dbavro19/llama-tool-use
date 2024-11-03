



import re
import streamlit as st

from misc_functions import call_llm, parse_xml, to_bool, get_bucket_name, download_file_from_s3_into_bytes


# ----------------------------------This Tool Takes for a Text or PDF Document and performs Processing on the Document Automatically  ----------------------------------
# ------------------------------------------------------- Toggle for Textract vs LLM ------------------------------------------------------------------


def get_math_tool():
    math = {
        "toolSpec": {
            "name": "calculator",
            "description": "A simple calculator that performs basic arithmetic operations. takes a mathematical expression and performs the calculations and returns an answer",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "expression":{
                            "type": "string",
                            "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4'). Make sure to use a valid expression and close any parenthesis"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    }
    return math


def calculator(expression):
    # Remove any non-digit or non-operator characters from the expression
    expression = re.sub(r'[^0-9+\-*/().]', '', expression)
    
    try:
        # Evaluate the expression using the built-in eval() function
        result = eval(expression)
        return str(result)
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError):
        return "Error: Invalid expression"