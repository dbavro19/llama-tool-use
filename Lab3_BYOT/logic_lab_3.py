import boto3
import json
import random
from botocore.config import Config
import re
from misc_functions import clean_and_convert_to_int
import tools_lab_3




#Invoke Bedrock via the Converse API
def converse_with_bedrock(messages, useTools=True, tool_definition=None, model_id="meta.llama3-1-405b-instruct-v1:0"):

    if tool_definition is None:
        tool_definition = tools_lab_3.get_tools()

    # Configure the client 
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

    # System prompt
    system_prompt = """
    You are a helpful AI assistant. Answer users questions accurately and concisely.
    You have been provided with a set of tools you can use. Use them when you can.
    Dont use tools and answer yourself if they are not needed
    """
    #Creating a Tool - Step 4: Guiding the model on how Strict Tool Use Is

    '''
    system_prompt = """
    You are a helpful AI assistant. Answer users questions accurately and concisely.
    You have been provided with a set of tools you can use. You must use these tools
    If there are no available tools relevant for the provided task respond with "Sorry, i dont have a tool for that"
    """
    '''

    # Ensure messages is a list
    if not isinstance(messages, list):
        messages = [messages]

    # Make the API call
    response = bedrock.converse(
        modelId=model_id,
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
        toolConfig={
            "tools": tool_definition
        },
        system=[{"text": system_prompt}],
        messages=messages
    )

    return response



#Parse the response from the model
def parse_response(response):
    print(f"Full Response: {response}")
    if response.get('stopReason') == 'tool_use':
        tool_use = next((item for item in response['output']['message']['content'] if 'toolUse' in item), None)
        if tool_use:
            return tools_lab_3.process_tool_use(tool_use['toolUse'])

    elif response.get('stopReason') == 'end_turn':
        assistant_text = response['output']['message']['content'][0]['text']
        if '{"type":"function"' in assistant_text.strip():
            return tools_lab_3.process_function_text(assistant_text)
        else:
            return assistant_text, "No Tool Used", "No Parameters Used"

    return None  # Return None if no condition is met



