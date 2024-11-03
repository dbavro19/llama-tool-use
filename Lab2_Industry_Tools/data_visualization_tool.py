import json
import plotly.express as px
import kaleido
import os
import pandas as pd
import sqlite3
import re
import streamlit as st
from misc_functions import call_llm, parse_xml

#STILL NEED TO FIX THE OUTPUT = CURRENTLY OPENS IN A NEW TAB AND I THINK THAT WILL BREAK Cloud9
#Fix COlor

def get_data_visualization():
    data_visualization = {
        "toolSpec": {
            "name": "data_visualization_tool",
            "description": "Retrieves Financial Trading System Data and provides a Graph or Chart for visualization of the data",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "requested_data": {
                            "type": "string",
                            "description": "The details of the requested data to be used to query the data source - ie. trade volume by portfolio or Account breakdown by asset type"
                        },
                        "visualization_type":{
                            "type": "string",
                            "description": "The type of visualization requested - valid values are: bar_chart, pie_chart, stacked_bar_chart, line_chart - use bar_chart as default if no visualization type is specified"
                        }
                    },
                    "required": ["requested_data", "visualization_type"]
                }
            }
        }
    }
    return data_visualization





def data_visualization_tool(requested_data, visualization_type='bar_chart', return_to_llm=False):


    #Get Schema - static - gets schema of the database
    schema = get_schema()

    st.write(f"Database Schema Discovered - ")
    st.write(schema)



    #Generate SQL Query based on requested data
    sql_query, expected_columns = generate_sql_query(requested_data, schema)

    st.write(f"SQL Query Generated - {sql_query}")

    #Execute SQL Query
    rows = execute_sql_query(sql_query)


    try:
        print("trying to set columns")
        expected_columns_collection = expected_columns.split(",").strip()
        rows_df = pd.DataFrame(rows, columns=expected_columns_collection)
    except:
        print("failed to set columns")
        rows_df = pd.DataFrame(rows)
    

    st.write(f"Query Results -")
    st.write(rows_df)

    #Generate visualization

    plotly = generate_plotly(requested_data,rows_df,visualization_type, expected_columns)

    st.write("Generated Visualization Code")
    st.code(plotly)

    #execute?

    fig, result_bool = execute_plotly(plotly, rows_df)

    if result_bool == True:
        result_type = "plotly"
    else:
        result_type = "text"


    return fig, result_type






def get_schema(trade_id=1):
    # Extract numeric value from trade_id if it's a string
    if isinstance(trade_id, str):
        # Try to extract a number from strings like "TR_(x)"
        match = re.search(r'\d+', trade_id)
        if match:
            trade_id = int(match.group())
        else:
            # If no numeric part found, try to convert the whole string to int
            try:
                trade_id = int(trade_id)
            except ValueError:
                print(f"Invalid trade_id format: {trade_id}")
                return None
    elif not isinstance(trade_id, int):
        try:
            trade_id = int(trade_id)
        except (ValueError, TypeError):
            print(f"Invalid trade_id format: {trade_id}")
            return None

    db_file = 'test_database.db'  # Adjust this path if needed

    # Connect to the SQLite database file
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Retrieve the column names
    cursor.execute("PRAGMA table_info(trade_blotter)")
    columns = [col[1] for col in cursor.fetchall()]

    # Retrieve data for the specified Trade_ID
    cursor.execute("SELECT * FROM trade_blotter WHERE Trade_ID = ?", (trade_id,))
    row = cursor.fetchone()

    # Close the database connection
    connection.close()

    # Check if a record was found
    if row is None:
        print(f"No data found for Trade_ID {trade_id}")
        return None

    # Create a DataFrame with the column names and data
    df = pd.DataFrame([row], columns=columns)


    return df



def generate_sql_query(user_request, schema):

    
    #Set System Prompt
    system_prompt=f"""
You are an Data Analytics AI Assistant
You will be provided with a question from the user, and the database schema of a Financial Trading System
Your task is to generate a valid sqlite query to retrieve the requested data

To do so you will do the following:
1. Understand the relevant information from the user question inclusive of the overall business context of the question
2. Analyze the database schema provided
3. Generate the executable sql query that will retrieve the data from the database

Here is the Database Schema:
<schema>
{schema}
</schema>

An example of a good sqlite query provided below:
<exmaple_query>
SELECT * FROM trade_blotter WHERE Trade_ID = 1
</exmaple_query>


Return the following in your response
Your full thought process in <thinking> xml tags
return a list (comma separated) of the expected columns that will be returned in <expected_columns> xml tags
The fully executable sql query in <sql_query> xml tags - paying extra attention to creating an accurate and valid sql query. No other text should be returned

"""
        

    #Set User Prompt
    user_prompt=f"""
    <user_request>
    {user_request}
    </user_request>
    """

    results = call_llm(system_prompt, user_prompt, model_id="us.meta.llama3-2-90b-instruct-v1:0")

    thinking = parse_xml(results, "thinking")
    expected_columns = parse_xml(results, "expected_columns")
    sql_query = parse_xml(results, "sql_query")


    return sql_query, expected_columns



def execute_sql_query(sql_query):
    # Connect to the SQLite database file
    db_file = 'test_database.db'  # Adjust this path if needed
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Execute the SQL query
    cursor.execute(sql_query)
    rows = cursor.fetchall()

    # Close the database connection
    connection.close()

    return rows



def generate_plotly(user_request, rows, chart_type, expected_columns):

    rows_str = str(rows.to_dict('records')).strip()




    example_plotly = """
# Grouping by Asset_Type and summing Quantity for Trade Volume by Asset Type
visual_dataframe = df.groupby('Asset_Type')['Quantity'].sum().reset_index()

# Creating a bar chart with automatic color coding by Asset_Type
fig = px.bar(
    visual_dataframe,
    x='Asset_Type',
    y='Quantity',
    color='Asset_Type',  # This adds automatic color by category
    title='Trade Volume by Asset Type',
    labels={'Quantity': 'Trade Volume', 'Asset_Type': 'Asset Type'}
)"""



    #Set System Prompt
    system_prompt=f"""
You are an Data Analytics AI Assistant
You will be provided with a question from the user, and the dataframe results from a database query answering that question
Your task is to generate a {chart_type} python plotly visualization code of the data that will provide a data visual to answer the user question

To do so you will do the following:
1. Understand the user question inclusive of the overall business context of the question
2. Analyze the data results from the <rows_df> pandas dataframe provided
4. Modify and manipulate the data in the dataframe as needed to generate the plotly visualization code
5. Create the executable Plotly visualization code for a {chart_type}
6. Create relevant labels and titles for the plotly visualization code

Here is the relevant dataframe:
<df>
{rows_str}
</df>

The column names that should be used are as follows:
<expected_columns>
{expected_columns}
</expected_columns>

An example of a good plotly graph:
<example_plotly>
{example_plotly}
</example_plotly>

The expected column names are

Note:
- You will only have access to the following libraries: plotly.express as px, pandas as pd
- Make sure to use different colors for better visualization and distinguishability
- Use the column names in expected column names as they are better formatted than the actual column names from the dataframe
- Always use the name visual_dataframe for the dataframe used in the plotly visualization code
- The provided dataframe you will manipulate if needed will always be named df
- Always use the variable fig for the plotly figure object
- do not include any additional data
- do not include any imports - code only
- do not include any text outside of the plotly visualization code
- return the value of the plotly code as a string


Return the following in your response
Your full thought process in <thinking> xml tags
The fully executable python plotly code in <final_plotly_code> xml tags as a plain string - paying extra attention to creating an accurate and valid plotly visualization. No other text should be returned

"""
        

    #Set User Prompt
    user_prompt=f"""
    <user_request>
    {user_request}
    </user_request>
    """

    

    results = call_llm(system_prompt, user_prompt, model_id="us.meta.llama3-2-90b-instruct-v1:0")

    thinking = parse_xml(results, "thinking")
    plotly_code = parse_xml(results, "final_plotly_code")

    return plotly_code


def execute_plotly(plotly_code, df):
    # Import statements needed for the plotly code to work
    import plotly.express as px
    import pandas as pd
    
    # Create a dictionary to serve as a local namespace
    # This acts like a container for variables that will be used in the exec() function
    local_dict = {
        'pd': pd,          # Makes pandas available to the executed code
        'px': px,          # Makes plotly express available to the executed code
        'df': df,          # Passes the input DataFrame to the executed code
        'fig': None        # Initializes fig variable that will store the plot
    }
    
    try:
        # exec() executes the string as Python code
        # globals() provides access to the global namespace
        # local_dict provides a local namespace for variables
        exec(plotly_code, globals(), local_dict)
        
        # Retrieve the figure object created in the executed code
        fig = local_dict['fig']
        
        # Display the figure (useful in notebooks/Streamlit)

        
        
        

            
        return fig, True
        
    except Exception as e:
        output = f"Error executing plotly code: {str(e)}"
        return output, False


