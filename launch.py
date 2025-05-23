#@title DeFooocus Custom Model Launch with Custom Download
#@markdown **Skip default model download & use your own model**

import os
import sys
import ssl

# Allow unverified SSL for downloads
ssl._create_default_https_context = ssl._create_unverified_context

# Memory and device configs
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
if "GRADIO_SERVER_PORT" not in os.environ:
    os.environ["GRADIO_SERVER_PORT"] = "7865"

# Debug launch args
print('[System ARGV] ' + str(sys.argv))

# ---------------------- Settings ----------------------
# Basic UI and performance flags
theme = "dark"  #@param ["dark", "light"]
preset = "default"  #@param ["default", "realistic", "anime", "lcm", "sai", "turbo", "lighting", "hypersd", "playground_v2.5", "dpo", "spo", "sd1.5"]
advanced_args = (
    "--share --attention-split --always-high-vram "
    "--disable-offload-from-vram --all-in-fp16 --lowvram --gpu-id 0"
)  # Added lowvram for memory
# Custom model definition: add more tuples for multiple custom models
custom_models = [
    {
        "url": (
            "https://civitai-delivery-worker-prod.5ac0637cfd0766c97916cefa3764fbdf."
            "r2.cloudflarestorage.com/model/6357/cyberrealisticxlplay.ohly.safetensors?"
            "X-Amz-Expires=86400&response-content-disposition=attachment%3B%20filename%3D%22"
            "cyberrealisticXL_v57.safetensors%22&X-Amz-Algorithm=AWS4-HMAC-SHA256"
        ),
        "name": "cyberrealisticXL_v57.safetensors",
        "dest_folder": "models/checkpoints"
    },
]
# ------------------------------------------------------

# Build CLI args
g_args = f"{advanced_args} --theme {theme}"
if preset != "default":
    g_args += f" --preset {preset}"

# ------------------ Environment Setup ------------------
from modules.launch_util import run, python

def prepare_environment():
    # Install PyTorch (with CUDA support)
    run(f'"{python}" -m pip install torch==2.1.0 torchvision==0.16.0 --extra-index-url https://download.pytorch.org/whl/cu121',
        "Installing torch & torchvision", live=True)
    # Install other requirements
    run(f"pip install -r requirements_versions.txt", "Installing requirements", live=False)

# Git clone and install DeFooocus
def setup_repo():
    run('pip install pygit2==1.12.2', "Installing pygit2")
    if not os.path.isdir('DeFooocus'):
        run('git clone https://github.com/imshubh99/DeFooocus', "Cloning DeFooocus")
    os.chdir('DeFooocus')
    run('pip install -r requirements_versions.txt', "Installing repo requirements")

# ------------------ Model Download ------------------
def download_custom_models():
    # Skip default model download
    open('skip_model_download.txt', 'a').close()

    # Ensure folders and download each custom model
    for m in custom_models:
        folder = os.path.join(os.getcwd(), m['dest_folder'])
        os.makedirs(folder, exist_ok=True)
        dest = os.path.join(folder, m['name'])
        if not os.path.exists(dest):
            print(f"Downloading custom model: {m['name']}")
            run(f'wget -O "{dest}" "{m["url"]}"', "Downloading model")

# ---------------------- Launch ----------------------
if __name__ == '__main__':
    prepare_environment()
    setup_repo()
    download_custom_models()

    # Start the UI using entry_with_update.py
    print("[DeFooocus] Starting with custom models ...")
    run(f"{python} entry_with_update.py {g_args}", "Launching DeFooocus UI")
