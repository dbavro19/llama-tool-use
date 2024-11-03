


import json
import os
import pandas as pd
import sqlite3
import re
import boto3
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import BedrockEmbeddings
import streamlit as st

from misc_functions import call_llm, parse_xml


# ----------------------------------This Tool Uses RAG to retrieve infomration from a knowledge Base ----------------------------------
# ------------------- This Tool Needs some setup. In Lab_2_Setup_scripts, run python .\faiss_setup.py - This setups the Vector Store and  database that will act as our trading system ---------------------


def get_insurance_policy_frequently_asked_questions():
    insurance_and_account_frequently_asked_questions = {
        "toolSpec": {
            "name": "insurance_policy_frequently_asked_questions",
            "description": "Retrieves answers for Insurance and Account information for user's insurance frequently asked questions ",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "user_question": {
                            "type": "string",
                            "description": "The full context of the user's question"
                        }
                    },
                    "required": ["user_question"]
                }
            }
        }
    }
    return insurance_and_account_frequently_asked_questions


def insurance_policy_frequently_asked_questions(user_question):
    st.write("Using RAG to Retrieve Relevant Answers")

    st.write(f"Embedding the Question: {user_question}")

    st.write(f"Querying the Vector Store for Similar Segments")

    query_results = query_faiss(user_question)

    st.write("Formatting Results")

    formatted_results = format_list(query_results)

    st.write(f"Formatted Results: \n{formatted_results}")

    st.write("Sending to LLM")

    llm_response = answer_with_llm(user_question, formatted_results)

    return llm_response







def query_faiss(user_question, k=3):
    """
    Query the FAISS index with a user question
    """
    try:
        # Setup paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        index_dir = os.path.join(current_dir, "document_faiss_index")  # Changed to look in current directory
        
        # Debug print
        st.write(f"Looking for FAISS index in: {index_dir}")
        
        # Check if directory exists
        if not os.path.exists(index_dir):
            st.error(f"Index directory not found at: {index_dir}")
            return []
            
        # Check for required files
        if not (os.path.exists(os.path.join(index_dir, "index.faiss")) and 
                os.path.exists(os.path.join(index_dir, "index.pkl"))):
            st.error("Missing required index files (index.faiss or index.pkl)")
            return []
        
        # Initialize Bedrock embeddings
        embeddings = BedrockEmbeddings(
            credentials_profile_name="default",
            region_name="us-west-2",
            model_id="amazon.titan-embed-text-v1"
        )
        
        # Load the FAISS index from the directory
        vectorstore = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
        
        # Perform similarity search
        docs = vectorstore.similarity_search(user_question, k=k)
        
        # Extract just the text content from the documents
        results = [doc.page_content for doc in docs]
        
        return results
        
    except Exception as e:
        st.error(f"Error querying FAISS index: {str(e)}")
        return []





def format_list(list):
    formatted_list_string = ""
    for item in list:
        if item != "UNDETERMINED":
            formatted_list_string += f"- {item}\n\n"
    return formatted_list_string


def answer_with_llm(user_question, context):
    
    system_prompt="""
You are an AI assistant that provides help with user's Insurance and Insurance Account Questions

Answer with the user's question with the context below. If the context does not provide a answer for the question, say so

Be concise and accurate in your answer

Replace all references to Allstate or Allstate Insurance with ACME or ACME insurance

"""

    user_prompt=f"""
<user_question>
{user_question}
</user_question>

<context>
{context}
</context>

"""


    llm_response = call_llm(user_prompt, system_prompt, model_id="us.meta.llama3-2-11b-instruct-v1:0")
    return llm_response