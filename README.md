# DataAgent

# Open AI API Keys
- Create your own config/local/credentials.yml file and fill the key

# Docker can be installed or:
1. Get the zipped version from https://download.docker.com/win/static/stable/x86_64/
2. Unzip and get the folder path
3. Set DOCKET_PATH variable in credentials with corresponding path


# Olama:
- Install Olama as Windows program
- Open cmd and run: ollama run llama2

- Download a model:
- Can retrieve HuggingFace models such: ollama run hf.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF:Q8_0
- Can manually download gguf file:
  - Download gguf model from: https://huggingface.co/leafspark/Llama-3.2-11B-Vision-Instruct-GGUF/tree/main
  - Get gguf and place it at: C:\Users\user\.ollama\models 
  - Create there a txt named Modelfile with content: FROM ./Llama-3.2-11B-Vision-Instruct.Q8_0.gguf
  - Open cmd and run: ollama create llama3.2.11B --file C:\Users\USER\.ollama\models\Modelfile.txt
  - run in the cdm as check: ollama list

Ensure GPU is enabled:
- Create or review file: C:\Users\TU_USUARIO\.ollama\config.toml
  - Need to contain:
[compute]
device = "cuda"
- run: ollama run llama3.2.11B or your downloaded model (check them with "ollama list")
- Check Ollama is running: http://localhost:11434






