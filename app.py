import streamlit as st
import os
import glob
from src.agents import process_message, create_agents_crewai

agent = create_agents_crewai()
st.title("Public OpenAI chatbot - non sensitive data usage")

# Upload logic
UPLOAD_FOLDER = os.path.join(os.getcwd(), "data", "input")
if os.path.exists(UPLOAD_FOLDER):
    for f in glob.glob(f'{UPLOAD_FOLDER}/*'):
        os.remove(f)
else:
     os.makedirs(UPLOAD_FOLDER)

col1, col2 = st.columns([1, 2])
with col1:
    st.header("File Upload")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File saved at {save_path}")
            st.write(f"**Name:** {uploaded_file.name}")
            #st.write(f"**Size:** {len(uploaded_file.getvalue())} bytes")
    else:
        st.info("No file updated yet.")

with col2:
    st.header("ChatBot")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Your message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = process_message(agent, prompt)
                st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})




