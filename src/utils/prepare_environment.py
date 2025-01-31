import os
import subprocess
from pathlib import Path
from omegaconf import OmegaConf
import shutil
import time
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

    if clean_memory:
        try:
            utils.remove_files("data/memory_chroma_db/")
        except:
            time.sleep(5)
            utils.remove_files("data/memory_chroma_db/")
    merged_configs['memory_config'] = {
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "chatbot_memory",
                "path": f"data/memory_chroma_db",
            },
        },
    }

    #docker_path = define_docker_path(merged_configs['credentials'].get('DOCKER_PATH',''))
    #prepare_docker(docker_path)

    return merged_configs

def set_api_keys():

    config = get_config()
    for k, v in config['credentials']['API_KEYS'].items():
        print(f"Setting up environment variable: {k}")
        os.environ[k] = v

    #if 'DOCKER_PATH' in config['credentials'].keys():
    #    docker_path = config['credentials']['DOCKER_PATH']
    #    os.environ["PATH"] += os.pathsep + Path(docker_path).as_posix()
        # shutil.which("docker")


def find_docker_installed():
    """Intenta encontrar Docker en el sistema usando 'where docker'."""
    try:
        docker_exe = subprocess.check_output(["where", "docker"], universal_newlines=True).strip()
        if docker_exe:
            return os.path.dirname(docker_exe.split("\n")[0])  # Devuelve la carpeta donde está docker.exe
    except subprocess.CalledProcessError:
        return None  # No encontrado

def define_docker_path(docker_portable_path=''):
    # Buscar Docker en el sistema
    docker_installed_path = find_docker_installed()

    # Determinar qué versión usar
    if docker_installed_path:
        docker_path = docker_installed_path
        print("Usando Docker instalado en:", docker_path)
    elif os.path.exists(os.path.join(docker_portable_path, "docker.exe")):
        docker_path = docker_portable_path
        print("Usando Docker portable en:", docker_path)
    else:
        raise FileNotFoundError("No se encontró Docker instalado ni portable.")

    # Agregar la ruta seleccionada al PATH temporalmente
    os.environ["PATH"] += os.pathsep + docker_path

    # Verificar que Docker es accesible
    docker_exe = shutil.which("docker")
    if docker_exe:
        print("Docker encontrado en:", docker_exe)
        return docker_path
    else:
        raise RuntimeError("No se pudo encontrar Docker en el PATH.")


def prepare_docker(docker_path):

    def is_docker_running():
        """Verifica si Docker está en ejecución"""
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False  # Docker no está en el PATH

    def start_docker():
        """Inicia Docker Daemon (dockerd.exe) si no está corriendo"""
        dockerd_path = os.path.join(docker_path, "dockerd.exe")
        if not os.path.exists(dockerd_path):
            raise FileNotFoundError("dockerd.exe no encontrado en " + docker_path)

        print("Iniciando Docker...")
        subprocess.Popen([dockerd_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_CONSOLE)

    # Verificar si Docker está corriendo, si no, iniciarlo
    if not is_docker_running():
        start_docker()

    # Verificar nuevamente después de unos segundos
    time.sleep(5)
    if is_docker_running():
        print("Docker está en ejecución.")
    else:
        raise RuntimeError("No se pudo iniciar Docker. Inténtalo manualmente.")
