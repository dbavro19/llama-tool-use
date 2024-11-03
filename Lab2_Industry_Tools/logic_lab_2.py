import boto3
import json
import random
from botocore.config import Config
import re
import tools_lab_2
from misc_functions import parse_text_function_response, generate_tooluse_id




#Invoke Bedrock via the Converse API - meta.llama3-1-405b-instruct-v1:0
#anthropic.claude-3-haiku-20240307-v1:0
def converse_with_bedrock_with_tools(messages, file=None, tool_definition=None, model_id="meta.llama3-1-405b-instruct-v1:0"):

    if tool_definition is None:
        tool_definition = tools_lab_2.get_tools()

    # Configure the client 
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

    # System prompt
    system_prompt = """
    You are a helpful AI assistant. Answer users questions accurately and concisely with the tools provided, using the tool_use format expected of the Bedrock Converse API

    You must use the tools provided unless you are summarizing an answer from a previous tool call
    You are not allowed to write code
    """


    # Ensure messages is a list
    if not isinstance(messages, list):
        messages = [messages]

    # Make the API call

    body = {
        "modelId": model_id,
        "inferenceConfig": {
            "maxTokens": 4096,
            "temperature": 0
        },
        "toolConfig": {
            "tools": tool_definition
        },
        "system": [{"text": system_prompt}],
        "messages": messages
    }

    response = bedrock.converse(**body)




    #response = bedrock.converse(
    #    modelId=model_id,
    #    inferenceConfig={
    #        "maxTokens": 2000,
    #        "temperature": 0
    #    },
    #    toolConfig={
    #        "tools": tool_definition
    #   },
    #    system=[{"text": system_prompt}],
    #    messages=messages
    #)

    return response



#Invoke Bedrock via the Converse API - meta.llama3-1-405b-instruct-v1:0
#anthropic.claude-3-haiku-20240307-v1:0
def converse_with_bedrock_without_tools(messages, file=None, model_id="meta.llama3-1-405b-instruct-v1:0"):


    # Configure the client 
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

    # System prompt
    system_prompt = """
    Provide an answer to the user's question based on the results of the tool that was executed
    """


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
        system=[{"text": system_prompt}],
        messages=messages
    )

    return response





#Parse the response from the model
def parse_response(response, message_list = None):
    print(f"Full Response: {response}")
    if response.get('stopReason') == 'tool_use':
        
        # Parse the JSON string into a Python dictionary
        try:
            data = json.loads(response)
        except:
            print("Error parsing JSON - trying it directly")
            data=response

        # Extract the desired values
        try:
            tool_used=True
            true_tool_use = True
            tool_use_id = data['output']['message']['content'][0]['toolUse']['toolUseId']
            tool_name = data['output']['message']['content'][0]['toolUse']['name']
            input_params = data['output']['message']['content'][0]['toolUse']['input']
            answer = None
        except:
            tool_used=True
            true_tool_use = True
            tool_use_id = data['output']['message']['content'][1]['toolUse']['toolUseId']
            tool_name = data['output']['message']['content'][1]['toolUse']['name']
            input_params = data['output']['message']['content'][1]['toolUse']['input']
            answer = None



    elif response.get('stopReason') == 'end_turn':
        assistant_text = response['output']['message']['content'][0]['text']
        if '{"type":"function"' in assistant_text.strip():
            #Add logic to parse the function name, 
            '''
            {'ResponseMetadata': {'RequestId': 'd1ab4893-63d0-4bfb-aaaa-8482e004a865', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Sun, 27 Oct 2024 13:52:49 GMT', 'content-type': 'application/json', 'content-length': '397', 'connection': 'keep-alive', 'x-amzn-requestid': 'd1ab4893-63d0-4bfb-aaaa-8482e004a865'}, 'RetryAttempts': 0}, 'output': {'message': {'role': 'assistant', 'content': [{'text': '\n\n<|python_tag|>{"type":"function","name":"get_stock_price","parameters":"stock_symbol": "AAPL","get_52_week_details": "True","return_to_llm": "False","user_question": "What is Apple"}}'}]}}, 'stopReason': 'end_turn', 'usage': {'inputTokens': 495, 'outputTokens': 48, 'totalTokens': 543}, 'metrics': {'latencyMs': 4572}}
            '''
            temp_results = parse_text_function_response(assistant_text.strip())

            tool_used=True
            true_tool_use = False
            tool_name = "invalid tool name"
            tool_use_id = "invalid tool id"
            input_params = "invalid parameters"
            answer = None

        
        else:
            tool_used=False
            true_tool_use = False
            tool_name = "No Tool Used"
            tool_use_id = "No Tool Used"
            input_params = "No Parameters Used"
            answer = assistant_text.strip()

    return tool_used, true_tool_use, tool_name, tool_use_id, input_params, answer






