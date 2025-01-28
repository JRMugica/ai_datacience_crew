import os
from mem0 import Memory, MemoryClient
import streamlit as st
from src.agents import  create_agents_crewai
import src.utils as utils


st.title("Public OpenAI chatbot - non sensitive data usage")

if "started" not in st.session_state:
    st.session_state.config = utils.get_config(clean_memory=True)
    utils.set_api_keys()
    st.session_state.memory = Memory.from_config(st.session_state.config['memory_config'])  # uses Open AI
    st.session_state.messages = []
    st.session_state.started = True

col1, col2 = st.columns([1, 2])
with col1:
    st.header("File Upload")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if uploaded_files == []:
        utils.remove_files(st.session_state.config['UPLOAD_FOLDER'])
        st.info("No file updated yet.")
    else:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(st.session_state.config['UPLOAD_FOLDER'], uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File saved at {save_path}")
            st.write(f"**Name:** {uploaded_file.name}")

with col2:
    st.header("ChatBot")
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])

    if user_input := st.chat_input("Your message"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            st.session_state.memory.add(f"User: {user_input}", user_id="user")
        with st.spinner("Thinking..."):
            relevant_info = st.session_state.memory.search(query=user_input, limit=3, user_id="user")
            context = "\n".join(message["memory"] for message in relevant_info)
            inputs = {
                    "user_message": f"{user_input}",
                    "context": f"{context}",
            }
            answer = create_agents_crewai().kickoff(inputs=inputs).raw
        with st.chat_message("assistant"):
            if ("import" in answer) & ('plotly' in answer):
                code = answer.replace('```','').replace('python\n','')
                exec(code)
                st.plotly_chart(fig)
            st.write(answer)
            st.session_state.memory.add(f"Assistant: {answer}", user_id="assistant")
            st.session_state.messages.append({"role": "assistant", "content": answer})




