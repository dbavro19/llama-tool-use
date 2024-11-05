import streamlit as st
import boto3
import json
from botocore.config import Config
#from Lab_Tools.basic_tools import get_tools, get_tools_pretty


# title of the streamlit app
st.title(f""":rainbow[Build Your Own Tool with Llama]""")


tool_name = st.text_input("Tool Name", key="tool_name")
tool_description = st.text_input("Tool Description", key="tool_description")
parameters_to_use = st.text_input("Parameters to Use", key="parameters_to_use")
parameter_descriptions = st.text_input("Parameter Descriptions", key="parameter_descriptions")
business_logic_description = st.text_area("Business Logic Description", key="business_logic_description")



# Configure the client
bedrock= boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2',
    config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
)


#sample tools
tool_sample_1 = {
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


tool_sample_2 = {
    "toolSpec": {
        "name": "trade_confirmation",
        "description": "Validates a trading email against the user's trading system and checks for validity and consistency",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "trade_id": {
                        "type": "string",
                        "description": "The identified trade_id value from the email - usually a number"
                    },
                    "email_contents":{
                        "type": "number",
                        "description": "The full contents of the provided email to be validated"
                    }
                },
                "required": ["trade_id", "email_contents"]
            }
        }
    }
}




#------------------------------------------ BUILD THE PYTHON FUNCTION ---------------------------------------------------------
def bedrock_define_function(tool_name,tool_spec, business_logic_description,  model_id="us.meta.llama3-2-90b-instruct-v1:0"):

    # Configure the client (assuming bedrock is already defined)
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

    # System prompt
    system_prompt = f"""
    <<SYS>>
    You are an AI developer who will take the business logic details and the LLM toolSpec json and build a functional python method

    Use the description of the desired business logic and the json toolSpec and use it to build the python code that will complete the task the tool is designed for

    The python code you create needs to follow the following rules:
    1. It must be a single python function
    2. It must be named the same as the toolSpec name
    3. It must take in the parameters specified in the toolSpec
    4. It should return a printable string (unless explicitly asked otherwise)
    5. It must only use the parameters specified in the toolSpec
    6. It should include the packages and imports in the python function
    7. Only common, or well known libraries should be used
    8. It must be fully executable and ready to run, all placeholder values should be commented out
    9. Comment each line of code describing its function
    10. Always include an import for the json library - it is needed to execute the code that you generate 
    11. Include "import streamlit as st" in the code - use st.write to log all the activity and actions the code takes
    12. Dont use any special characters in the code. Not text should require utf encoding


    return the python_function in <python_function> xml tags, returning only the code and no other text
    return a list of the additional libraries used / imported in <libraries> xml tags, returning only the code and no other text
    
    <<SYS>>
    """

    # Make the API call
    # Make the API call
    response = bedrock.converse(
    modelId=model_id,
    inferenceConfig={
        "maxTokens": 3000,
        "temperature": 0
    },
    system=[{"text": system_prompt}],
    messages=[{
        "role": "user",
        "content": [
            {
                "text": f"""
                <tool_name>{tool_name}</tool_name>

                <tool_spec>{tool_spec}</tool_spec>

                <business_logic_description>{business_logic_description}</business_logic_description>
                """
            }
        ]
    }]
)
    print(system_prompt)
    print("-------------")
    llm_output = parse_response(response)
    python_function = parse_xml(llm_output, "python_function")
    libraries = parse_xml(llm_output, "libraries")


    return python_function, libraries



#------------------------------------------ BUILD THE TOOL SPEC --------------------------------------------------------
def bedrock_define_tool(sample_tool_1, sample_tool_2, name, description, parameters_to_use, parameter_descriptions, business_logic_description,  model_id="us.meta.llama3-2-90b-instruct-v1:0"):

    # Configure the client (assuming bedrock is already defined)
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2',
        config=Config(retries={'max_attempts': 3, 'mode': 'standard'})
    )

    # System prompt
    system_prompt = f"""
    <<SYS>>
    You are an AI developer who will take details and description for an LLM tool and create the toolSpec json schema that will be used to call the tool

    Use the below <example_tools> for the structure and schema of the tool's json schema
    If the tool has parameters, make sure to include them in the json schema and the business logic code
    Key and value pairs should be encased in double quotes(")
    Parameters will be comma separated. Make sure you are using the right parameter details and descriptions
    If the tool does not have parameters, still include the json schema but leave the parameters section blank as per the example
    tool names should be lowercase and use underscores instead of spaces to make them easily parsable in json
    Credentials and API Keys CANNOT be used in the tool spec as parameters. they should be handled by the python method we will create later

    Use the parameter descriptions and business_logic_description to determine what inputs should be used. If the parameters described wont work with the business logic attempts to do, create better descirptions and parameters
    Try to keep it simple and straight forward

    Here are some examples - the format MUST match the examples json schema's
    <example_1>
    {sample_tool_1}
    </example_1>

    <example_2>
    {sample_tool_2}
    </example_2>


    
    return the json in <tool_json> xml tags with no other text
    
    <<SYS>>
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


    return tool_json



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


button = st.button("Generate Tool")

if button:
    tool_json = bedrock_define_tool(tool_sample_1, tool_sample_2, tool_name, tool_description, parameters_to_use, parameter_descriptions, business_logic_description)
    st.write("Tool Spec:")
    processed_json = tool_json.replace("'", "\"").strip()
    st.write(processed_json)


    st.write("-------------------------")

    python_function, libraries = bedrock_define_function(tool_name, processed_json, business_logic_description)




    #Adding get_tool method
    python_function = python_function + f"""
\n
def get_tool_method():
    my_tool_spec = '{processed_json}'
    my_tool_spec_json = json.loads(my_tool_spec)
    return my_tool_spec_json
\n
"""
    
    st.write("Code being added to my_tool.py:")
    st.code(python_function, language="python")

    st.write("-------------------------")

    st.write("Check that these libraries are installed:")
    st.code(libraries, language="python")



    

    
    #open my_tool.py file and write the python function to it
    with open("my_tool.py", "w") as f:
        f.write(python_function)

    st.write("-------------------------")
    st.write("my_tool.py Updated!")


