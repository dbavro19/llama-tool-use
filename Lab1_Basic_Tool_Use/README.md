# Lab 1: Introduction to Tool Use

## Overview
This lab covers the fundamentals of Tool use in an LLM-powered application. You'll learn about the Bedrock Converse API, work with a user interface, create custom tools, and understand how to guide model behavior through system prompts.

## Files in this Lab
- **frontend_lab1.py**: Contains the Front End Streamlit Logic for the GUI interface
- **logic_lab_1.py**: Contains the LLM model integration logic and structuring
- **tools_lab_1.py**: Contains Tool definitions, their corresponding logic, and execution code
- **misc_functions.py**: Handles miscellaneous functions (no modifications needed during the lab)

## Lab Steps

### Step 1: Introduction to the Bedrock Converse API
1. Open and review `logic_lab_1.py`
2. Examine the Converse API structure and model selection logic
3. Run the file from the Lab1_Basic_Tool_Use directory:
   ```bash
   python3 .\logic_lab_1.py
   ```
4. Review the terminal output

### Step 2: Starting the UI
1. Comment out the following line in `logic_lab_1.py`:
   ```python
   # test_run(message_1, message_2, message_3, model)
   ```
2. Launch the UI:
   ```bash
   streamlit run frontend_lab_1.py --server.port 8080 --server.enableXsrfProtection=False
   ```
3. Select "Preview Running Application Button" in your cloud9 environment
4. Test the application:
   - Try requesting random numbers with and without ranges
   - Ask general knowledge questions
   - Attempt to find edge cases (First person to break it wins a prize!)

### Step 3: Creating a New Tool
1. Stop the UI (Ctrl+C)
2. In `tools_lab_1.py`, uncomment the following:
   - Tool configuration for `hello_response_tool_def`
   - Add tool definition: `tool_definition.append(hello_response_tool_def)`
   - Implementation method: `def hello_response(user_name=None):`
3. Save all changes
4. Restart the UI using the command from Step 2

### Step 4: Guiding Model Tool Use
1. Modify the system prompt in `logic_lab_1.py`:
   - Either change the existing prompt
   - Or uncomment the alternative system prompt
2. Save changes
3. Restart the UI using the command from Step 2
4. Test and observe the behavioral differences

## Completion
Congratulations on completing Lab 1! You should now have a solid understanding of:
- Tool Use / Function Calling
- Bedrock Converse API integration
- Custom tool creation
- Model behavior modification through prompts

## Next Steps
Proceed to Lab 2 to explore industry-specific tools in action.
