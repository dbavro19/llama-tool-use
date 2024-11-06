import streamlit as st
import boto3
import botocore
import kaleido
import langchain
import numpy
import pandas
import plotly
import requests
import streamlit
import json
import os
import sqlite3
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import base64
import io

# title of the streamlit app
st.title(f""":rainbow[Building AI Tools for FSI with Llama]""")

bedrock = boto3.client('bedrock-runtime' , 'us-west-2')



def llama_bedrock_call(model_id="meta.llama3-1-405b-instruct-v1:0", max_gen_len=100):

    bedrock = boto3.client('bedrock-runtime' , 'us-west-2')

    
    system_prompt="""
<<SYS>>
You are responding to a user saying hello.
Greet the user, in a professional and very concise manner
Welcome them to the "AWS-META-FSI-Roadshow"
<<SYS>>

Hello!

"""
    


    prompt_template = {
            "prompt": system_prompt,
            "temperature": 0,
            "max_gen_len": max_gen_len
        }

    json_prompt = json.dumps(prompt_template)

    response = bedrock.invoke_model(body=json_prompt, modelId=model_id, accept="application/json", contentType="application/json")

    response_body = json.loads(response.get('body').read())

    print(f"response body: {response_body}")

    generation_text = response_body['generation']


    return generation_text


response = llama_bedrock_call()

st.write(response)
