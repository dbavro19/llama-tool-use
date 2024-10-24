import streamlit as st
from basic_tools import converse_with_bedrock, parse_response, process_tool_use, process_function_text, clean_and_convert_to_int, get_tools, get_tools_pretty, format_messages

# title of the streamlit app
st.title(f""":rainbow[Building AI Tools for FSI with Llama]""")

st.balloons()

with st.expander("Available Tools", expanded=True):
    tools = get_tools_pretty()
    for tool in tools:
        for name, description in tool.items():
            st.markdown(f"**{name}**: {description}")


 
userQuery = st.text_input("Ask A Question!")

button = st.button("Submit")

if button and userQuery:
    with st.chat_message("user"):
        st.markdown(userQuery)
    message = format_messages(userQuery)
    #st.session_state.messages.append(message)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.status("Answering!", expanded=True) as status:
            response = converse_with_bedrock(message)
            answer, tool = parse_response(response)
            message_placeholder.markdown(f""" Answer:
                            {answer}
                            """)
            status.update(label=f"Tool Used: {tool}", state="complete", expanded=False)
    #st.session_state.messages.append({"role": "assistant", "content": answer})




