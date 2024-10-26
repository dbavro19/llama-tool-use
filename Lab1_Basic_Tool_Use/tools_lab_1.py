import json
import random
import re
import sys
import inspect
from misc_functions import clean_and_convert_to_int


#Variable that will hold our Tool Configuration - Predefining our Tools for Lab 1
tool_definition = []

random_number_1_to_100_tool = {
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
    }

random_number = {
        "toolSpec": {
            "name": "random_number_with_inputs",
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

#Creating a Tool - Step 1: Define the Tool Specification
#Remove the below comments to enable a new tool that handles greetings
'''
hello_response_tool_def = {
        "toolSpec": {
            "name": "hello_response",
            "description": "Respond to the user saying Hello and other greetings - if you know the user's name provide that as an input parameter (optional)",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "user_name": {
                            "type": "string",
                            "description": "The name of the user to greet"
                        }
                    }
                }
            }
        }
    }
'''


#Add more tools here

#add tools to the tool definition array
tool_definition.append(random_number_1_to_100_tool)
tool_definition.append(random_number)

#Creating a Tool - Step 2: Add the tool to the list of available tools for the model
#Remove comment on the line below to add the new tool we created in Step 1

#tool_definition.append(hello_response_tool_def) 


#-----------------Tool Methods - add business logic here--------------------

#method to generate random number between 1 and 100
def random_number_1_to_100():
    random_number = random.randint(1, 100)
    return random_number

#method to generate random number within a specified range
def random_number_with_inputs(min, max):
    min = clean_and_convert_to_int(min)
    max = clean_and_convert_to_int(max)
    random_number = random.randint(min, max)
    return random_number

#Creating a Tool - Step 3: Add the tool to the list of available tools for the model
#Remove comment on the line below to add the new tool we created in Step 1
'''
def hello_response(user_name=None):
    if user_name is None or not user_name:
        user_name = 'User'
    greeting = f"Hello {user_name}! How are you today? - Welcome to the AWS - Meta GenAI Summit Series"
    return greeting
'''


#----------------Calling Tools - How the tools get called---------------------


#Process tool use
def old_process_tool_use(tool_use):
    print("-----------------------Processing Tool Use----------------------")
    print(tool_use)
    print("-----------------------Done----------------------")
    tool_name = tool_use['name']

    if tool_name == 'random_number_1_to_100':
        random_number = random_number_1_to_100()
        return random_number, tool_name

    elif tool_name == 'random_number_with_inputs':
        min_val = clean_and_convert_to_int(tool_use['input']['min'])
        max_val = clean_and_convert_to_int(tool_use['input']['max'])
        print(f"min: {min_val}, max: {max_val}")
        random_number = random_number_with_inputs(min_val, max_val)
        return random_number,tool_name
    
    #Adds handling to Call the hello_response Method - REMOVE to activate
    '''
    elif tool_name == 'hello_response':
        user_name = tool_use.get('input', {}).get('user_name')
        greeting = hello_response(user_name)
        return greeting, tool_name
    '''


def process_tool_use(tool_use):
    tool_name = tool_use['name']
    input_params = tool_use.get('input', {})

    # Get the current module
    current_module = sys.modules[__name__]

    # Check if the function exists in the current module
    if hasattr(current_module, tool_name):
        tool_function = getattr(current_module, tool_name)
        
        # Get the function's parameters
        sig = inspect.signature(tool_function)
        params = sig.parameters

        # Prepare the arguments
        args = {}
        parameters_used = {}
        for param_name, param in params.items():
            if param_name in input_params:
                # If the parameter is in the input, use it
                if param.annotation == int:
                    # Only use clean_and_convert_to_int for parameters annotated as int
                    args[param_name] = clean_and_convert_to_int(input_params[param_name])
                else:
                    args[param_name] = input_params[param_name]
                parameters_used[param_name] = args[param_name]
            elif param.default is not inspect.Parameter.empty:
                # If the parameter has a default value, use it
                args[param_name] = param.default
                parameters_used[param_name] = args[param_name]
            else:
                # If the parameter is required but not provided, raise an error
                raise ValueError(f"Required parameter '{param_name}' not provided for tool '{tool_name}'")

        # Call the function with the prepared arguments
        result = tool_function(**args)
        return result, tool_name, parameters_used
    else:
        raise ValueError(f"Tool '{tool_name}' not found")




#Process end turn function calling - Catches an edge case that the tool use comes back a s a string
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


#----------------Helper Functions -------------------------------------------

def get_tools():
    return tool_definition

def get_tools_pretty():
    # Parse tool name and tool definitions
    tool_json = get_tools()
    return [{tool['toolSpec']['name']: tool['toolSpec']['description']} for tool in tool_json]