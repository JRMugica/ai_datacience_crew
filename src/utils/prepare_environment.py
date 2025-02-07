import os
import subprocess
from pathlib import Path
from mem0 import Memory, MemoryClient
from omegaconf import OmegaConf
import shutil
import time
import torch
import src.utils as utils

def get_config(base_dir='config/base', local_dir='config/local', clean_memory=False):
    merged_configs = {}

    base_path = Path(os.getcwd()).joinpath(base_dir)
    local_path = Path(os.getcwd()).joinpath(local_dir)
    conf_files = list(set(os.listdir(base_path)+os.listdir(local_path)))
    for filename in conf_files:
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            base_path_file = os.path.join(base_path, filename)
            local_path_file = os.path.join(local_path, filename)

            if os.path.exists(local_path_file):
                local_conf = OmegaConf.load(local_path_file)
                if os.path.exists(base_path_file):
                    base_conf = OmegaConf.load(base_path_file)
                    merged_conf = OmegaConf.merge(base_conf, local_conf)
                else:
                    merged_conf = local_conf
            else:
                base_conf = OmegaConf.load(base_path_file)
                merged_conf = base_conf

            merged_configs[filename.split('.')[0]] = merged_conf

    merged_configs['UPLOAD_FOLDER'] = Path(os.path.join(os.getcwd(), merged_configs['parameters']['UPLOAD_FOLDER']))
    merged_configs['MEMORY_FOLDER'] = Path(os.path.join(os.getcwd(), merged_configs['parameters']['MEMORY_FOLDER']))

    merged_configs['memory_config'] = {
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "chatbot_memory",
                "path": f"data/memory_chroma_db",
            },
        },
    }

    return merged_configs

def set_api_keys(config):

    for k, v in config['credentials']['API_KEYS'].items():
        print(f"Setting up environment variable: {k}")
        os.environ[k] = v

def get_memory(config, clean_memory=False):

    if clean_memory:
        try:
            utils.remove_files(config['memory_config']["vector_store"]["config"]["path"])
        except:
            time.sleep(5)
            try:
                utils.remove_files(config['memory_config']["vector_store"]["config"]["path"])
            except:
                pass

    return Memory.from_config(config['memory_config'])

def get_available_gpus():
    if torch.cuda.is_available():
        return [f"GPU {i}: {torch.cuda.get_device_name(i)}" for i in range(torch.cuda.device_count())]
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True)
        gpus = result.stdout.strip().split("\n")
        return [f"Local model on GPU {i}: {gpu}" for i, gpu in enumerate(gpus)]
    except Exception:
        return ["No local GPU available"]

def get_ollama_models():
    # Run the Ollama command to list installed models
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)

    # Check if the command was successful and print the result
    if result.returncode == 0:
        print("Installed Ollama Models:")
        print(result.stdout)
        return [s.split(' ')[0] for s in result.stdout.split('\n') if s!=''][1:]
    else:
        print("Error occurred while checking installed ollama models.")
        print(result.stderr)
        return []
