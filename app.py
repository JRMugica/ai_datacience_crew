import streamlit as st
import os
from src.agents import  create_agents_crewai
from src.utils import clean_input_files, read_config, excel_to_csv

# Prepare setup
config = read_config()
UPLOAD_FOLDER = os.path.join(os.getcwd(), config['parameters']['UPLOAD_FOLDER'])

st.title("Public OpenAI chatbot - non sensitive data usage")

col1, col2 = st.columns([1, 2])
with col1:
    st.header("File Upload")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

    #if uploaded_files is None:
    clean_input_files(config)
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File saved at {save_path}")
            st.write(f"**Name:** {uploaded_file.name}")
            #st.write(f"**Size:** {len(uploaded_file.getvalue())} bytes")
        excel_to_csv(config)
    else:
        st.info("No file updated yet.")

crew = create_agents_crewai()
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




