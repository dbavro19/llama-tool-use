# AWS Bedrock Workshop - Lab 3: Build Your Own Tools

In this lab, we'll focus on building custom tools. You can either build tools independently or use our Llama-powered tool generator for assistance.

## Getting Started

First, change to the Lab3 directory:
```bash
cd Lab3_BYOT
```

Launch the tool generator:
```bash
streamlit run tool_generator.py --server.port 8080 --server.enableXsrfProtection=False --server.enableCORS=False
```

## Using the Tool Generator

Fill in the following fields in the UI:
- Tool Name
- Tool Description
- Parameters to Use (comma-separated for multiple)
- Parameter Descriptions (comma-separated for multiple)
- Business Logic Description (include expected input, workflow details, and output)

Click the "Generate Tool" button to automatically generate code in `my_tool.py`.

> Note: While the generator handles most cases well, some elements (like API keys) will be added as placeholders.

### Example Tool Generation

Tool Name:
```plaintext
get_weather
```

Tool Description:
```plaintext
Retrieves the weather for a specified city
```

Parameters to Use:
```plaintext
city
```

Parameter Descriptions:
```plaintext
The name of the city for the weather request
```

Business Logic Description:
```plaintext
Takes the city name as input, calls an api to get the weather for that city, formats the results, and returns a string of the formatted weather results
```


## Implementing Your Tool

1. Check generated code in `my_tool.py`
2. Install any required packages (contact lab assistant if needed)
3. Modify `tools_lab_3.py` to import your tool:

```python
from my_tool import get_tool_method, tool_method_name_change_this  # ADD your business logic method name (same as tool_name)
```

One other thing to note, any time your function would call an API, the model will not provide the API key. So if your get weather app is using the OpenWeather API, you can use this key

> Note: OpenWeather API, you can use this key:
```plaintext
89d3c1f4adc6d1c49259fa7ba18f24e7
```


## Testing Your Tool

Stop the current Streamlit session with Control+C

Launch the tool testing UI:
```bash
streamlit run frontend_lab_3.py --server.port 8080 --server.enableXsrfProtection=False --server.enableCORS=False
```

## Technical Reference

### Tool Schema Template
```json
{
    "toolSpec": {
        "name": "tool_name",
        "description": "Detailed tool description",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "input_parameter_1": {
                        "type": "data type (string, number etc.)",
                        "description": "Description of the input parameter"
                    },
                    "input_parameter_2":{
                        "type": "data type (string, number etc.)",
                        "description": "Description of the input parameter"
                    }
                },
                "required": ["input_parameter_1 (but only if its required)","input_parameter_1 (but only if its required)"]
            }
        }
    }
}
```

## Additional Notes

1. Add your generated toolSpec to the model's expected list in `tools_lab_3.py`
2. You have access to various AWS services through IAM permissions - feel free to leverage them in your tool logic
3. The business logic generator provides most of the implementation, but you may need to add specific elements like API keys or authentication tokens

