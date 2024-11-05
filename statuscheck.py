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

# title of the streamlit app
st.title(f""":rainbow[Building AI Tools for FSI with Llama]""")

st.header("Everything Looks Good!")