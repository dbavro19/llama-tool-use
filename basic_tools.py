import boto3
import json
import random
from botocore.config import Config
import re
from tool_methods import random_number_with_inputs, random_number_1_to_100

# Configure the client
bedrock= boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2',
    config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
)



#Invoke Bedrock via the Converse API
def converse_with_bedrock(messages, tool_definition=None, model_id="meta.llama3-1-405b-instruct-v1:0"):

    if tool_definition is None:
        tool_definition = get_tools()

    # Configure the client (assuming bedrock is already defined)
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
    if response.get('stopReason') == 'tool_use':
        tool_use = next((item for item in response['output']['message']['content'] if 'toolUse' in item), None)
        if tool_use:
            return process_tool_use(tool_use['toolUse'])

    elif response.get('stopReason') == 'end_turn':
        assistant_text = response['output']['message']['content'][0]['text']
        if '{"type":"function"' in assistant_text.strip():
            return process_function_text(assistant_text)
        else:
            print(f"Assistant: {assistant_text}")
            return assistant_text, "No Tool Used"

    return None  # Return None if no condition is met

#Process tool use
def process_tool_use(tool_use):
    tool_name = tool_use['name']

    if tool_name == 'random_number_1_to_100':
        random_number = random_number_1_to_100()
        return random_number, tool_name

    elif tool_name == 'random_number':
        min_val = clean_and_convert_to_int(tool_use['input']['min'])
        max_val = clean_and_convert_to_int(tool_use['input']['max'])
        print(f"min: {min_val}, max: {max_val}")
        random_number = random_number_with_inputs(min_val, max_val)
        return random_number,tool_name

#Process end turn function calling
def process_function_text(text):
    # Extract the JSON part from the text
    print(text)
    match = re.search(r'\{.*\}', text)
    print(match)
    if match:
        
        function_json = json.loads(match.group())
        function_name = function_json['name']
        print(f"Function called: {function_name}")

        if function_name == 'random_number_1_to_100':
            random_number = random_number_1_to_100()
            return random_number

        elif function_name == 'random_number':
            min_val = clean_and_convert_to_int(function_json.get('min', 1))
            max_val = clean_and_convert_to_int(function_json.get('max', 1))
            print(f"min: {min_val}, max: {max_val}")
            random_number = random_number_with_inputs(min_val, max_val)
            return random_number


    return None

def clean_and_convert_to_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # Remove spaces and commas
        cleaned = re.sub(r'[,\s]', '', value)
        return int(cleaned)
    raise ValueError(f"Unable to convert {value} to int")



def get_tools():
    return tool_definition

def get_tools_pretty():
    # Parse tool name and tool definitions
    tool_json = get_tools()
    return [{tool['toolSpec']['name']: tool['toolSpec']['description']} for tool in tool_json]


def format_messages(user_input):
    message = [
    {
        "role": "user",
        "content": [{"text": user_input}]
    }
    ]
    return message


tool_definition = [
    {
        "toolSpec": {
            "name": "random_number_1_to_100",
            "description": "Generate a random number between 1 and 100 - use this as the default number generation tool if no minimum or maximum range is specified",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "random_number",
            "description": "Generate a random number within a specified range",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "The specified minimum value for the random number"
                        },
                        "max": {
                            "type": "number",
                            "description": "The specified maximum value for the random number"
                        }
                    },
                    "required": ["min", "max"]
                }
            }
        }
    }
]






#No tool use
message_1 = [
    {
        "role": "user",
        "content": [{"text": "What is the capital of France"}]
    }
]

#Tool with no parameters
message_2 = [
    {
        "role": "user",
        "content": [{"text": "Give me a random number"}]
    }
]

#Tool with parameters
message_3 = [
    {
        "role": "user",
        "content": [{"text": "Give me a random number between 5 and 9"}]
    }
]


#model= "meta.llama3-8b-instruct-v1:0"
#model= "meta.llama3-70b-instruct-v1:0"
model= "meta.llama3-1-405b-instruct-v1:0"
#model= "meta.llama3-1-70b-instruct-v1:0"
#model= "meta.llama3-1-8b-instruct-v1:0"
#model= "us.meta.llama3-2-11b-instruct-v1:0"
#model= "us.meta.llama3-2-1b-instruct-v1:0"
#model= "us.meta.llama3-2-3b-instruct-v1:0"
#model= "us.meta.llama3-2-90b-instruct-v1:0"
#model= "anthropic.claude-3-haiku-20240307-v1:0"
#model="us.anthropic.claude-3-opus-20240229-v1:0"



#response = converse_with_bedrock(message_1, tool_definition, model)
#print("Simple Test - What is the capital of France")
#print("")
#print(response)
#print("")
#parsed_response = parse_response(response)

#print("-------------------------------------------")
#print("Simple Tool - random number")
#print("")
#response = converse_with_bedrock(message_2, tool_definition, model)
#print(response)
#print("-------------------------------------------")
#parsed_response = parse_response(response)

#print("-------------------------------------------")



#print("Complex Tool - random number with min and max")
#print("")
#response = converse_with_bedrock(message_3, tool_definition, model)
#print(response)
#print("-------------------------------------------")
#parsed_response = parse_response(response)




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





def test_run(message_1, message_2, message_3, tool_definition, model):
    # Simple Test
    response = converse_with_bedrock(message_1, tool_definition, model)
    print_clean_response("Simple Test - What is the capital of France", response)

    # Simple Tool - random number
    response = converse_with_bedrock(message_2, tool_definition, model)
    print_clean_response("Simple Tool - random number", response)
    parsed_response, tool_used = parse_response(response)
    if parsed_response:
        print(f"Random number generated: {parsed_response}")
    print("-------------------------------------------")

    # Complex Tool - random number with min and max
    response = converse_with_bedrock(message_3, tool_definition, model)
    print_clean_response("Complex Tool - random number with min and max", response)
    parsed_response = parse_response(response)
    if parsed_response:
        print(f"Random number generated: {parsed_response}")
    print("-------------------------------------------")


#test_run(message_1, message_2, message_3, tool_definition, model)

