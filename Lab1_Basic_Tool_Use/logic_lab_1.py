import boto3
import json
import random
from botocore.config import Config
import re
from misc_functions import clean_and_convert_to_int
import tools_lab_1




#Invoke Bedrock via the Converse API
def converse_with_bedrock(messages, useTools=True, tool_definition=None, model_id="meta.llama3-1-405b-instruct-v1:0"):

    if tool_definition is None:
        tool_definition = tools_lab_1.get_tools()

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
            return tools_lab_1.process_tool_use(tool_use['toolUse'])

    elif response.get('stopReason') == 'end_turn':
        assistant_text = response['output']['message']['content'][0]['text']
        if '{"type":"function"' in assistant_text.strip():
            return tools_lab_1.process_function_text(assistant_text)
        else:
            return assistant_text, "No Tool Used", "No Parameters Used"

    return None  # Return None if no condition is met






#No tool use
message_1 = [
    {
        "role": "user",
        "content": [{"text": "What is the capital of France, use provided tools if needed. Dont use tools if you dont need them"}]
    }
]

#Tool with no parameters
message_2 = [
    {
        "role": "user",
        "content": [{"text": "Give me a random number, use provided tools if needed. Dont use tools if you dont need them"}]
    }
]

#Tool with parameters
message_3 = [
    {
        "role": "user",
        "content": [{"text": "Give me a random number between 5 and 9, use provided tools if needed. Dont use tools if you dont need them"}]
    }
]








def print_clean_response(title, response):
    print(f"\n{title}")
    print("-------------------------------------------")
    
    if 'output' in response and 'message' in response['output']:
        content = response['output']['message'].get('content', [])
        if isinstance(content, list) and content:
            if 'text' in content[0]:
                print(content[0]['text'].strip())
            elif 'toolUse' in content[0]:
                tool_use = content[0]['toolUse']
                print(f"Using tool: {tool_use['name']}")
                if 'input' in tool_use:
                    print(f"Input: {tool_use['input']}")
    
    print("-------------------------------------------")


#-------------Below Sections are for Testing Only ---------------

model= "meta.llama3-1-405b-instruct-v1:0"

def test_run(message_1, message_2, message_3, model):
    # Simple Test
    response = converse_with_bedrock(message_1, model)
    print_clean_response("Simple Test - What is the capital of France", response)

    # Simple Tool - random number
    response = converse_with_bedrock(message_2, model)
    print_clean_response("Simple Tool - random number", response)
    parsed_response, tool_used, parameters_used = parse_response(response)
    if parsed_response:
        print(f"Random number generated: {parsed_response}")
    print("-------------------------------------------")

    # Complex Tool - random number with min and max
    response = converse_with_bedrock(message_3, model)
    print_clean_response("Complex Tool - random number with min and max", response)
    parsed_response, tool_used, parameters_used = parse_response(response)
    if parsed_response:
        print(f"Random number generated: {parsed_response}")
    print("-------------------------------------------")

#Run
#Comment the below line out when finished
test_run(message_1, message_2, message_3, model)

