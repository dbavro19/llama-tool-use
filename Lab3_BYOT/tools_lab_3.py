import json
import random
import re
import sys
import inspect
from misc_functions import clean_and_convert_to_int
from my_tool import get_tool_method ,get_weather # - ADD your business logic method name (it will be the same as your tool_name!)# , 




tool_definition = []
tool_definition.append(get_tool_method())




#----------------Calling Tools - How the tools get called---------------------


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




#----------------Helper Functions -------------------------------------------

def get_tools():
    return tool_definition

def get_tools_pretty():
    # Parse tool name and tool definitions
    tool_json = get_tools()
    return [{tool['toolSpec']['name']: tool['toolSpec']['description']} for tool in tool_json]