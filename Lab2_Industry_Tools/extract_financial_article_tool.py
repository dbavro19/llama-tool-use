import json
import streamlit as st
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from misc_functions import call_llm, parse_xml


# ----------------------------------This tool takes a provided url, reads the website and if its a financial article, parses some key metrics ----------------------------------
# ------------------- Try it with This article about Amazon: https://www.fool.com/investing/2024/10/21/5-reasons-to-buy-amazon-stock-like-theres-no-tomor/ ---------------------


def get_extract_financial_article():
    get_extract_financial_article = {
        "toolSpec": {
            "name": "extract_financial_article",
            "description": "Retrieves information from a web article or online financial report by reading the web_url provided, and extracts key financial metrics from the article.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "web_url": {
                            "type": "string",
                            "description": "The user provided website url"
                        }
                    },
                    "required": ["web_url"]
                }
            }
        }
    }
    return get_extract_financial_article



def extract_financial_article(web_url, return_to_llm=False):

    st.write(f"Reading Financial Article from: {web_url}")


    response = parse_url(web_url)
    if response == "Error: Unable to parse the provided url":
        st.write("Error: Unable to parse the provided url")
        return response
    

    else:

        st.write("Sending to LLM to Extract and Format")

        #Set System Prompt
        system_prompt=f"""
You are a Financial Research Assistant
You will be provided with teh content of a financial article or report. Your task is to generate a concise summary of the call and extract some key metrics, including any key takeaways or significant events.
You will also be provided with a template for the expected json output. 
The output should be formatted according to the template in valid json


The template is as follows:
<sample_template>
[
  {{
    "title": "(A brief, descriptive title for the earnings call or financial event)",
    "date": "(The date of the earnings call or financial event in YYYY-MM-DD format)",
    "url": "(The original URL of the earnings call or financial event)",
    "source": "(Categorize the source material (Independent Financial Article, Earnings Call, Financial Report, etc.))",
    "summary": "(A concise summary of the main points discussed in the earnings call or financial event, typically 2-3 sentences)",
    "keyMetrics": [
      "(Quantitative metric - summary)",
      "(Specific Quantitative metric - specific (like YoY growth, stock price, etc.))"
    ],
    "takeaways": [
      "(A high-level conclusion about the company's or financial instrument's performance or strategy)",
      "(Sentiment analysis (Positive, Mixed, Negative) on the outlook of the subject))",
      "(Brief insight into why the Sentiment is what it is)"
    ],
  }},
]
</sample_template>

Think through each step in you think and return your thoughts in <thinking> xml tags with no other text
return the json output in <results> xml tag with no other text
"""
        

        #Set User Prompt
        user_prompt=f"""
        Article or Report content of url {web_url}  below:

        transcript: {str(response)}
        """

        results = call_llm(system_prompt, user_prompt, model_id="us.meta.llama3-2-11b-instruct-v1:0")
        results_output = parse_xml(results, "results")

        try:
            json_results_output = json.loads(results_output)
            print(f"Converting to JSON: {json_results_output}")
            answer_type = "json"
        except:
            json_results_output = results_output
            print(f"Error converting to JSON - so using this instead: {json_results_output}")
            answer_type = "text"


        for item in json_results_output:
            for key, value in item.items():
                st.write(f"**{key}:** {value}")
                st.write("---")  # Add a separator between items



    return json_results_output, answer_type


def truncate_string(string, max_length=100):
    return (string[:max_length] + '...') if len(string) > max_length else string


def parse_url(link):
    try:
        url =[link.strip()]
        loader = AsyncHtmlLoader(url)
        docs = loader.load()

        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)

        return docs_transformed[0].page_content
    except:
        return "Error: Unable to parse the provided url"
    



