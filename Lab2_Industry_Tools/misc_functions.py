#File for some helper functions that are used throughout the project

import re
import json
import random
import string
import boto3
import botocore





#Chat_history

question_history = []

###########################################################################################
### ----------LAB2 SETUP: Change this Method to add your bucket name here! ------------####
###########################################################################################
def get_bucket_name():

    bucket_name = "dome-test-meta-lab-12345" #Change this line to be YOUR bucket name that you created as part of the setup
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


# ------------- Base LLM Tool with configurable system prompt ----------------------

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




def parse_text_function_response(assistant_text):

    print(f"IT DID THE END_TURN THING! - Input Text: {assistant_text}")

    # Extract the JSON-like part from the text
    string_split = assistant_text.split('<|python_tag|>')

    print(f"string_split[1]: {string_split[1]}")

    if len(string_split) < 2:
        raise ValueError("No valid function call found in the text")

    json_str = string_split[1]
    json_str = json_str.strip()

    # Remove any trailing '}' as it might be duplicated
    json_str = json_str.rstrip('}')

    # Fix the "parameters" field to be a proper JSON object
    json_str = json_str.replace('"parameters":', '"parameters":{')
    json_str += '}'  # Close the parameters object
    json_str += '}'  # Close the main JSON object
    json_str = json_str.replace('=', ':')

    # Replace single quotes with double quotes, and add quotes around parameter names
    json_str = re.sub(r"(\w+):", r'"\1":', json_str)

    try:
        results = json.loads(json_str)
        return results

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None



def to_bool(value):
    if isinstance(value, bool):
        return value
    return value.lower() in ('true')


def parse_xml(xml, tag):
  start_tag = f"<{tag}>"
  end_tag = f"</{tag}>"
  
  start_index = xml.find(start_tag)
  if start_index == -1:
    return ""

  end_index = xml.find(end_tag)
  if end_index == -1:
    return ""

  value = xml[start_index+len(start_tag):end_index]
  return value




def generate_tooluse_id():
    # Define the parts of the ID
    prefix = "tooluse_"
    random_part_length = 16
    separator = "-"
    
    # Generate the random part
    characters = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(characters) for _ in range(random_part_length))
    
    # Insert the separator at a random position in the second half
    split_point = random.randint(8, 15)
    random_part = random_part[:split_point] + separator + random_part[split_point:]
    
    # Combine the parts
    tooluse_id = prefix + random_part
    
    return tooluse_id




def format_user_messages(user_input, document=None, file_name=None, file_type=None):
    if not document:
        message ={
            "role": "user",
            "content": [{"text": user_input}]
        }
        return message
    

    else:

        message ={
            "role": "user",
            "content": [{"text": f"{user_input} : \n Uploaded {file_type} document {file_name}"}]
        }

        return message



def format_assistant_messages(user_input, document=None):
    message ={
        "role": "assistant",
        "content": [{"text": user_input}]
    }
    return message

def format_tool_response_message(response):
    message = {
    "role": "user",
    "content": [
        {
            "toolResult": {
                "toolUseId": "tooluse_kZJMlvQmRJ6eAyJE5GIl7Q",
                "content": [
                        {
                        "text": response
                        }
                    ]
                }
            }
        ]
    }
    return message


def spoof_tool_response(tool_use_id, tool_name,input_parameters):
    message = {
            "role": "assistant",
            "content": [
                {
                    "toolUse": {
                        "toolUseId": tool_use_id,
                        "name": tool_name,
                        "input": input_parameters
                    }
                }
            ]
    }

    return message



def spoof_tool_user_message(tool_use_id, answer_type,tool_answer):

    if isinstance(tool_answer, dict):
        fixed_type = 'json'
    else:
        fixed_type = 'text'
        tool_answer = str(tool_answer)




    message = {
    "role": "user",
    "content": [
        {
            "toolResult": {
                "toolUseId": tool_use_id,
                "content": [
                    {
                        fixed_type: tool_answer
                    }
                ]
            }
        }
    ]
}

    return message
    



def get_model():
    model = "meta.llama3-1-405b-instruct-v1:0"
    backup_tool_model = "anthropic.claude-3-haiku-20240307-v1:0"
    return backup_tool_model





#Cleans and Strip whitespace of Numeric values when expecting integers
def clean_and_convert_to_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # Remove spaces and commas
        cleaned = re.sub(r'[,\s]', '', value)
        return int(cleaned)
    raise ValueError(f"Unable to convert {value} to int")

