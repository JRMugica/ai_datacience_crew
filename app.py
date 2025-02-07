import os
import streamlit as st
from src.agents import  create_agents_crewai
import src.utils as utils

st.set_page_config(layout="wide")
st.title("Chatbot Assistant - non sensitive data usage")
st.subheader("Only share sensitive data if local GPU usage")

if not st.session_state.get("started", False):
    st.session_state.started = True
    st.session_state.config = utils.get_config(clean_memory=True)
    utils.set_api_keys(st.session_state.config)
    st.session_state.memory = utils.get_memory(st.session_state.config, clean_memory=True)
    st.session_state.messages = []

col1, col2 = st.columns([1, 2])
with col1:
    st.header("Select model to use")
    model_choice = 'External OpenAI API (data sensitive)'
    gpus = utils.get_available_gpus()
    gpu_choice = st.selectbox("Choose a model:", [model_choice] + gpus)
    if 'GPU' in gpu_choice:
        models = utils.get_ollama_models()
        model_choice = st.selectbox("Select a local model:", models)

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
    st.header(f"ChatBot: {model_choice}")
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                if ("import" in message["content"]) & ('plotly' in message["content"]) & ('fig' in message["content"]):
                    try:
                        st.plotly_chart(fig)
                    except:
                        st.markdown(message["content"])
                else:
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
            answer = create_agents_crewai(model_choice).kickoff(inputs=inputs).raw
        with st.chat_message("assistant"):
            if os.path.exists('data/input/results_python_script.py'):
                with open("data/input/results_python_script.py", 'r') as f:
                    code = f.read()#.replace('\n', '')
                if ("import" in code) & ('plotly' in code) & ('fig' in code):
                    code = code.replace('```','').replace('python\n','')
                    exec(code)
                    st.plotly_chart(fig)
                    os.remove("data/input/results_python_script.py")
            st.write(answer)
            st.session_state.memory.add(f"Assistant: {answer}", user_id="assistant")
            st.session_state.messages.append({"role": "assistant", "content": answer})




