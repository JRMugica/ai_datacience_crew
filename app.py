import streamlit as st
import os
from src.agents import  create_agents_crewai
import src.utils as utils

# Prepare setup
config = utils.read_config()
UPLOAD_FOLDER = os.path.join(os.getcwd(), config['parameters']['UPLOAD_FOLDER'])

st.title("Public OpenAI chatbot - non sensitive data usage")

col1, col2 = st.columns([1, 2])
with col1:
    st.header("File Upload")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

    if uploaded_files == []:
        utils.remove_files(UPLOAD_FOLDER)
        st.info("No file updated yet.")
    else:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File saved at {save_path}")
            st.write(f"**Name:** {uploaded_file.name}")
            #st.write(f"**Size:** {len(uploaded_file.getvalue())} bytes")

crew = create_agents_crewai()
with col2:
    st.header("ChatBot")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]
    # Display chat messages for the current thread
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "agent":
            with st.chat_message("assistant"):
                st.markdown(message["content"])

    if prompt := st.chat_input("Your message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                inputs = {
                    **{'message':prompt,}
                }
                answer = crew.kickoff(inputs=inputs).raw
                if ("import" in answer) & ('plotly' in answer):
                    code = answer.replace('```','').replace('python\n','')
                    exec(code)
                    st.plotly_chart(fig)
                st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})




