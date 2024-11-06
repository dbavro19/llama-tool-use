#File for some helper functions that are used throughout the project

import re
import boto3
import botocore




#Chat_history

question_history = []


##################################################################################################################
### -LAB3 SETUP: Change this Method to add your bucket name here! If your tool is going to upload documents -####
###################################################################################################################
def get_bucket_name():

    bucket_name = "Bucket Name" #Change this line to be YOUR bucket name that you created as part of the setup
    return bucket_name



def trim_chat_history(messages):
    if len(messages) <= 6:
        return messages
    print("Trimming chat history - OVER 6 messages")
    sorted_messages = sorted(messages.items(), key=lambda x: int(x[0]))
    recent_messages = dict(sorted_messages[2:])  # Remove oldest pair

    for key, message in recent_messages.items():
        print(f"{key}: {message}")

    return recent_messages


    # Function to get the next available key
def get_next_key(messages):
    return max(messages.keys(), default=-1) + 1





def format_user_messages(user_input, document=None):
    message ={
        "role": "user",
        "content": [{"text": user_input}]
    }
    return message

def format_assistant_messages(user_input, document=None):
    message ={
        "role": "assistant",
        "content": [{"text": user_input}]
    }
    return message


#Cleans and Strip whitespace of Numeric values when expecting integers
def clean_and_convert_to_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # Remove spaces and commas
        cleaned = re.sub(r'[,\s]', '', value)
        return int(cleaned)
    raise ValueError(f"Unable to convert {value} to int")


def call_llm(user_prompt, system_prompt=None, file=None, model_id="meta.llama3-1-405b-instruct-v1:0"):


    # Configure the client 
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )

    # System prompt
    if system_prompt == None:
        system_prompt = """
        You are a helpful AI assistant. Answer the user's question accurately and concisely 
        """

    formatted_message = format_user_messages(user_prompt)

    converted_message = [formatted_message]

    # Make the API call
    response = bedrock.converse(
        modelId=model_id,
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
        system=[{"text": system_prompt}],
        messages=converted_message
    )

    text_value = response['output']['message']['content'][0]['text']



    return text_value
    

#Uploads file to S3 Bucket
def upload_file_to_s3(file, bucket_name, object_name=None):
    if object_name is None:
        object_name = file.name.strip()

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_fileobj(file, bucket_name, object_name)
    except botocore.exceptions.ClientError as e:
        print(f"Error uploading file to S3: {e}")

    return object_name


def download_file_from_s3_local(bucket_name, object_name, file_path=None):

    if file_path is None:
        file_path = object_name

    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(bucket_name, object_name, file_path)
    except botocore.exceptions.ClientError as e:
        print(f"Error downloading file from S3: {e}")
              
    return file_path

def download_file_from_s3_into_bytes(bucket_name, object_name):

    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        file_content = response['Body'].read()
        return file_content
    except botocore.exceptions.ClientError as e:
        print(f"Error downloading file from S3: {e}")
        file_content=None
              
    return file_content
