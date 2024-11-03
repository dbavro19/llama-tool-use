


import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import boto3
import io
import base64
import json
from langchain_community.document_loaders import PyPDFLoader
import streamlit as st

from misc_functions import call_llm, parse_xml, to_bool, get_bucket_name, download_file_from_s3_into_bytes


# ----------------------------------This Tool Takes for a Text or PDF Document and performs Processing on the Document Automatically  ----------------------------------
# ------------------------------------------------------- Toggle for Textract vs LLM ------------------------------------------------------------------


def get_intelligent_document_processor():
    document_processor = {
        "toolSpec": {
            "name": "intelligent_document_processor",
            "description": "Processes a pdf or image document or form file and extracts key information from the document. Useful for documents like pay stubs, drivers licenses, tax forms, and insurance claims - returns structured json",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "string",
                            "description": "the file name (and extension) of the document to process"
                        },
                    },
                    "required": ["file"]
                }
            }
        }
    }
    return document_processor


def intelligent_document_processor(file):

    file_type = file.split(".")[-1]

    bucket = get_bucket_name()

    image = download_file_from_s3_into_bytes(bucket, file)

    st.write("Processing Image Document with Llama")
    st.image(image)


    category, thinking, confidence = llama_with_image(image, file_type, system_prompt=set_category_prompt(),model_id = "us.meta.llama3-2-11b-instruct-v1:0", max_gen_len=100, parse_value="category")

    st.write(f"Document Category: {category}")

    if category == "Other" or None:
        results = {
        "Category": "Other",
        "Response": "Document isn't of an approved document type, please try a Auto Insurance Claim, Pay Stub, W2, or Drivers License"
    }
        
        return results

    else:
        results, thinking, confidence = llama_with_image(image, file_type, set_prompt(category))

        st.write(results)

        if confidence=="Medium" or confidence=="Low":
            st.markdown(f"**WARNING!** Model Confidence is {confidence}")
            st.write(f"Though Process: {thinking}")

        json_results = json.loads(results)

        for key, value in json_results.items():
            st.markdown(f"**{key}**: *{value}*")
            st.divider()

        return json_results

    




def llama_with_image(image, file_type, system_prompt, model_id = "us.meta.llama3-2-90b-instruct-v1:0", max_gen_len = 1000, parse_value = "json_results"):

    bedrock = boto3.client('bedrock-runtime' , 'us-west-2')

    
    # Check if the input is already bytes
    if isinstance(image, bytes):
        base64_string = base64.b64encode(image).decode('utf-8')
        
    else:
        # If it's a PIL Image, convert it to base64
        buffer = io.BytesIO()
        image.save(buffer, format=file_type)
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')

    


    prompt_template = {
            "prompt": system_prompt,
            "temperature": 0,
            "max_gen_len": max_gen_len,
            "images": [base64_string]
        }

    json_prompt = json.dumps(prompt_template)

    response = bedrock.invoke_model(body=json_prompt, modelId=model_id, accept="application/json", contentType="application/json")

    response_body = json.loads(response.get('body').read())

    print(f"response body: {response_body}")

    generation_text = response_body['generation']

    final_results=parse_xml(generation_text, parse_value)
    try:
        thinking=parse_xml(generation_text, "thinking")
        confidence=parse_xml(generation_text, "confidence")
    except:
        thinking = None
        confidence = None


    return final_results, thinking, confidence




def set_prompt(category):

    if category == "Auto Insurance Claim":
        system_prompt=f"""
<<SYS>>
You are a Data Analyst. 
Your task is to Extract the following information from the {category}
    -Name
    -Address
    -Date
    -Amount
    -Policy Number
    -Vehicle Make
    -Vehicle Model
    -Vehicle Year

If you cant find the above information for any category respond with "Not Found" for that category

Return your results in a json format using the example below
<exmaple_format>
{{
    "Name": "(Full Name)",
    "Address": "(Full Address)",
    "Date": "(Date)",
    "Amount": "($Amount)",
    "Policy_Number": "(Policy Number)",
    "Vehicle_Make": "(Vehicle Make)",
    "Vehicle_Model": "(Vehicle Model)",
    "Vehicle_Year": "(Vehicle Year)"

}}
</example_format>

You will also return your level of Confidence that the results are accurate and complete. This can be affected by image clarity or missing data. Return a value of High, Medium, or Low. Be honest and accurate in your rating. Medium and Low scores will be human reviewed

Think through each step of your thought process and write your thoughts down in <thinking> xml tags
return the valid json array in <json_results> xml tags, with no other text
return your level of <confidence> xml tags with no other text

<</SYS>>

Process this {category} document and return the information

"""

    elif category == "Drivers License":
        system_prompt=f"""
<<SYS>>
You are a Data Analyst.
Your task is to Extract the following information from the {category}
    -State
    -Full Name
    -Date of Birth
    -License Number
    -Expiration Date
    -Address
    -Donor Status
    -Veteran Status

If you cant find the above information for any category respond with "Not Found" for that category

Return your results in a json format using the example below
<example_format>
{{
    "Name": "(Full Name)",
    "Address": "(Full Address)",
    "Date": "(Date)",
    "Amount": "($Amount)",
    "Policy_Number": "(Policy Number)",
    "Vehicle_Make": "(Vehicle Make)",
    "Vehicle_Model": "(Vehicle Model)",
    "Vehicle_Year": "(Vehicle Year)"

}}
</example_format>

You will also return your level of Confidence that the results are accurate and complete. This can be affected by image clarity or missing data. Return a value of High, Medium, or Low. Be honest and accurate in your rating. Medium and Low scores will be human reviewed

Think through each step of your thought process and write your thoughts down in <thinking> xml tags
return the valid json array in <json_results> xml tags, with no other text
return your level of <confidence> xml tags with no other text

<</SYS>>

Process this {category} document and return the information

"""
        
    elif category == "Pay Stub":
        system_prompt=f"""
<<SYS>>
You are a Data Analyst
Your task is to Extract the following information from the {category}
    -Employee Name
    -Employee Address
    -Pay Period Start Date
    -Pay Period End Date
    -Gross Pay
    -Net Pay
    -Company
    -Company Address


If you cant find the above information for any category respond with "Not Found" for that category

Return your results in a json format using the example below
<example_format>
{{
    "Employee_Name": "(Employee Name)",
    "Employee_Address": "(Employee Address)",
    "Pay_Period_Start_Date": "(Pay Period Start Date)",
    "Pay_Period_End_Date": "(Pay Period End Date)",
    "Gross_Pay": "($ Gross Pay)",
    "Net_Pay": "($ Net Pay)",
    "Company_Name": "(Company Name)",
    "Company_Address": "(Company Address)"
}}
</example_format>




Think through each step of your thought process

return the valid json array in <json_results> xml tags, with no other text

<</SYS>>

Process this {category} document and return the information

"""
        
    elif category == "W2":
        system_prompt=f"""
<<SYS>>
You are a Data Analyst
Your task is to Extract the following information from the {category}
    -Tax Year
    -Employee Name
    -Employee Address
    -Employee Identification Number
    -Social Security (NOTE: YOU CAN ONLY USE THE LAST 4 DIGITS OF THE SSN FOR THIS CATEGORY)
    -Wages Tips and Other Compensation
    -Social Security Wages
    -Medicare Wages
    -Federal Tax Withheld
    -Social Security Taxes Withheld
    -Medicare Taxes Withheld
    -Social Security Taxes Withheld
    -Medicare Taxes Withheld
    -State and Local Taxes Withheld
    -State
    -State ID




If you cant find the above information for any category respond with "Not Found" for that category

Return your results in a json format using the example below
<example_format>
{{
    "Employee_Name": "(Employee Name)",
    "Employee_Address": "(Employee Address)",
    "Tax_Year": "(Tax_Year)",
    "Employee_ID": "(Employee ID Number)",
    "SSN_Last_Four": "(Last 4 digits of SSN)",
    "Tax_Year": "(Tax Year)",
    "Wages_Tips_Other_Compensation": "($ Amount)",
    "Social_Security_Wages": "($ Amount)",
    "Medicare_Wages": "($ Amount)",
    "Federal_Tax_Withheld": "($ Amount)",
    "Social_Security_Tax_Withheld": "($ Amount)",
    "Medicare_Tax_Withheld": "($ Amount)",
    "State_Tax_Withheld": "($ Amount)",
    "Local_Tax_Withheld": "($ Amount)",
    "State": "(State)",
    "State_ID": "(State ID Number)",
    "Company_Name": "(Company Name)",
    "Company_Address": "(Company Address)",
}}
</example_format>


You will also return your level of Confidence that the results are accurate and complete. This can be affected by image clarity or missing data. Return a value of High, Medium, or Low. Be honest and accurate in your rating. Medium and Low scores will be human reviewed

Think through each step of your thought process and write your thoughts down in <thinking> xml tags
return the valid json array in <json_results> xml tags, with no other text
return your level of <confidence> xml tags with no other text

<</SYS>>

Process this {category} document and return the information

"""
        
    else:
        system_prompt="""Something went wrong, fail gracefully"""



    return system_prompt


def set_category_prompt():
    system_prompt="""
<<SYS>>
You are a Data Analyst.
Your task is Classify the provided image document into a category
Valid Categories are:
     -Auto Insurance Claim
     -Drivers License
     -Pay Stub
     -W2
     -Other



return the category in <category> xml tags. Do not include any other text in your response

<</SYS>>

Process this image document and return the category with no other text
"""
    return system_prompt









def parse_xml(xml, tag):
    temp=xml.split(">")
    
    tag_to_extract="</"+tag

    for line in temp:
        if tag_to_extract in line:
            parsed_value=line.replace(tag_to_extract, "")
            return parsed_value