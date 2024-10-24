import streamlit as st
import boto3
import botocore
from botocore.config import Config
#from Lab_Tools.basic_tools import get_tools, get_tools_pretty

# Configure the client
bedrock= boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2',
    config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
)


#sample tools
sample_1 = {
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

sample_2 = {
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


#Invoke Bedrock via the Converse API
def bedrock_create_tool(sample_tool_1, sample_tool_2, name, description, parameters_to_use, parameter_descriptions, business_logic_description,  model_id="meta.llama3-1-405b-instruct-v1:0"):

    # Configure the client (assuming bedrock is already defined)
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

    # System prompt
    system_prompt = f"""
    You are an AI developer who will take details and description for an LLM tool and create the tools json and business logic code to implement the functionality described in python
    Make sure the code and the json is valid and directly executable, dont use placeholders or variables that need to be replaced

    Use the below <example_tools> for the structure and schema of the tool's json
    If the tool has parameters, make sure to include them in the json schema and the business logic code
    Parameters will be comma separated. Make sure you are using the right parameter details and descriptions
    If the tool does not have parameters, still include the json schema but leave the parameters section blank as per the example

    <example_tools>
    {sample_tool_1}
    
    {sample_tool_2}
    </example_tools>

    return the json in <tool_json> xml tags with no other text
    return the business logic code in <business_logic> xml tags with no other text
    """

    # Make the API call
    # Make the API call
    response = bedrock.converse(
    modelId=model_id,
    inferenceConfig={
        "maxTokens": 2000,
        "temperature": 0
    },
    system=[{"text": system_prompt}],
    messages=[{
        "role": "user",
        "content": [
            {
                "text": f"""
                <tool_name>{name}</tool_name>
                <tool_description>{description}</tool_description>
                <parameters_to_use>{parameters_to_use}</parameters_to_use>
                <parameter_descriptions>{parameter_descriptions}</parameter_descriptions>
                <business_logic_description>{business_logic_description}</business_logic_description>
                """
            }
        ]
    }]
)
    print(system_prompt)
    print("-------------")
    llm_output = parse_response(response)
    tool_json = parse_xml(llm_output, "tool_json")
    business_logic = parse_xml(llm_output, "business_logic")

    return tool_json, business_logic

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


#Parse the response from the model
def parse_response(response):


    response.get('stopReason') == 'end_turn'
    assistant_text = response['output']['message']['content'][0]['text']

    return assistant_text  # Return None if no condition is met


tool_name = "Get weather"
tool_description = "Gets the weather for the provided location"
parameters_to_use = "location"
parameter_descriptions = "zip code of the location provided"
business_logic_description = "Call the weather.com API with a zip code as the function input"


tool_json, business_logic = bedrock_create_tool(sample_1, sample_2, tool_name, tool_description, parameters_to_use, parameter_descriptions, business_logic_description)

print(tool_json)
print(business_logic)