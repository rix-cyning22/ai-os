#!/usr/bin/env python3
import os
import subprocess
import shutil
import re
import sys

def log(message):
    print(f"{message}")

def check_conda():
    """Check if Conda is installed, and install it if not."""
    if shutil.which("conda"):
        log("Conda is already installed.")
    else:
        log("Conda is not installed. Installing Miniconda...")
        miniconda_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        os.system(f"wget {miniconda_url} -O Miniconda3.sh")
        os.system("bash Miniconda3.sh -b -p $HOME/miniconda")
        os.system("rm Miniconda3.sh")
        os.system("export PATH=$HOME/miniconda/bin:$PATH")
        log("Conda installation complete.")

def env_exists(env_name):
    """Check if a conda environment with the given name already exists."""
    try:
        output = subprocess.check_output("conda env list", shell=True, text=True)
        for line in output.splitlines():
            if line.startswith(env_name + " ") or line.startswith(env_name + "\t"):
                return True
    except subprocess.CalledProcessError as e:
        log(f"Error checking environments: {e}")
    return False

def create_conda_env(env_name, py_version):
    """Create a new Conda environment with the given name and Python version."""
    log(f"Creating Conda environment: {env_name} with Python {py_version}")
    ret = os.system(f"conda create --name {env_name} python={py_version} -y")
    if ret != 0:
        raise Exception("Failed to create Conda environment.")
    log(f"Environment '{env_name}' created.")

def check_cuda():
    """
    Check if CUDA is installed by running 'nvidia-smi'.
    Returns a tuple (cuda_found, cuda_version) where cuda_version is a string like '12.1' if found.
    """
    try:
        result = subprocess.check_output("nvidia-smi", shell=True, text=True)
        match = re.search(r"CUDA Version:\s+(\d+\.\d+)", result)
        if match:
            cuda_version = match.group(1)
            log(f"CUDA detected. Version: {cuda_version}. GPU acceleration is available.")
            return True, cuda_version
    except subprocess.CalledProcessError:
        log("nvidia-smi command failed; CUDA not found.")
    except Exception as e:
        log(f"Error checking CUDA: {e}")
    log("CUDA not found. GPU acceleration is unavailable.")
    return False, None

def install_pytorch(env_name, use_cuda, cuda_version=None):
    """Install PyTorch in the specified Conda environment based on CUDA availability."""
    log("Installing PyTorch...")
    try:
        if use_cuda and cuda_version:
            log(f"Installing GPU-enabled PyTorch for CUDA {cuda_version} using Conda...")
            ret = os.system(f"conda install -n {env_name} pytorch torchvision torchaudio pytorch-cuda={cuda_version} -c pytorch -c nvidia -y")
            if ret != 0:
                log("Conda installation for PyTorch failed. Falling back to pip installation.")
                pip_cuda = "cu" + cuda_version.replace(".", "")
                os.system(f"conda run -n {env_name} pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/{pip_cuda}")
        else:
            log("Installing CPU-only PyTorch using Conda...")
            ret = os.system(f"conda install -n {env_name} pytorch torchvision torchaudio cpuonly -c pytorch -y")
            if ret != 0:
                log("Conda installation for CPU-only PyTorch failed. Falling back to pip installation.")
                os.system(f"conda run -n {env_name} pip install torch torchvision torchaudio")
        log("PyTorch installation complete.")
    except Exception as e:
        log(f"Failed to install PyTorch: {e}")

def install_tensorflow(env_name, use_cuda):
    """Install TensorFlow in the specified Conda environment based on CUDA availability."""
    log("Installing TensorFlow...")
    try:
        if use_cuda:
            log("Installing GPU-enabled TensorFlow using Conda...")
            ret = os.system(f"conda install -n {env_name} tensorflow -c conda-forge -y")
            if ret != 0:
                log("Conda installation for TensorFlow failed. Falling back to pip installation.")
                os.system(f"conda run -n {env_name} pip install tensorflow")
        else:
            log("Installing CPU-only TensorFlow using Conda...")
            ret = os.system(f"conda install -n {env_name} tensorflow-cpu -c conda-forge -y")
            if ret != 0:
                log("Conda installation for CPU-only TensorFlow failed. Falling back to pip installation.")
                os.system(f"conda run -n {env_name} pip install tensorflow-cpu")
        log("TensorFlow installation complete.")
    except Exception as e:
        log(f"Failed to install TensorFlow: {e}")

def install_requirements(env_name):
    """Ask the user for a requirements.txt file and install it using pip if provided."""
    req_path = input("Enter the path to a requirements.txt file to install (leave blank to skip): ").strip()
    if req_path:
        if os.path.exists(req_path):
            log(f"Installing packages from {req_path} using pip...")
            os.system(f"conda run -n {env_name} pip install -r {req_path}")
            log("Requirements installation complete.")
        else:
            log("File not found. Skipping requirements installation.")

def install_additional_packages(env_name):
    """Prompt user for additional packages to install and install them in the Conda environment."""
    additional = input("Do you want to install any additional packages? (y/n): ").strip().lower()
    if additional == 'y':
        packages = input("Enter package names separated by space: ").strip()
        if packages:
            log(f"Installing additional packages using Conda: {packages}")
            ret = os.system(f"conda install -n {env_name} {packages} -y")
            if ret != 0:
                log("Conda installation for additional packages failed. Falling back to pip installation.")
                os.system(f"conda run -n {env_name} pip install {packages}")
            log("Additional packages installation complete.")
        else:
            log("No package names entered. Skipping additional package installation.")
    else:
        log("No additional packages will be installed.")

def remove_conda_env(env_name):
    """Remove the Conda environment if created."""
    log(f"Removing Conda environment: {env_name}")
    os.system(f"conda env remove --name {env_name} -y")
    os.system("conda clean --all")
    log(f"Environment '{env_name}' removed.")

def main():
    env_created = False
    env_name = ""
    try:
        check_conda()
        
        # Prompt for the environment name
        env_name = input("Enter the Conda environment name: ").strip()
        if env_exists(env_name):
            log(f"Environment '{env_name}' already exists.")
            # Display the Python version of the existing environment.
            try:
                py_ver = subprocess.check_output(f"conda run -n {env_name} python --version", shell=True, text=True).strip()
                log(f"Python version in '{env_name}': {py_ver}")
            except subprocess.CalledProcessError as e:
                log(f"Could not retrieve Python version for '{env_name}': {e}")
        else:
            # Define valid Python version prefixes for this setup.
            valid_python_versions = ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12', '3.13']
            py_version = input(f"Enter Python version (valid options start with: {', '.join(valid_python_versions)}): ").strip()
            while not any(py_version.startswith(v) for v in valid_python_versions):
                log(f"Invalid Python version: {py_version}.")
                py_version = input(f"Please enter a valid Python version (valid options start with: {', '.join(valid_python_versions)}): ").strip()
            create_conda_env(env_name, py_version)
            env_created = True
        
        install_pytorch_choice = input("Do you want to install PyTorch? (y/n): ").strip().lower() == 'y'
        install_tensorflow_choice = input("Do you want to install TensorFlow? (y/n): ").strip().lower() == 'y'
        
        cuda_found, cuda_version = check_cuda()
        if cuda_found:
            choice = input(f"CUDA detected (version: {cuda_version}). Do you want to proceed with CPU-only versions? (y/n): ").strip().lower()
            if choice == 'y':
                log("User opted for CPU-only versions despite CUDA being available.")
                use_cuda = False
            else:
                log("User opted for GPU-enabled versions.")
                use_cuda = True
        else:
            choice = input("CUDA is not installed. Do you want to proceed with CPU-only versions? (y/n): ").strip().lower()
            if choice != 'y':
                log("Exiting setup as GPU drivers and CUDA are not available.")
                raise Exception("CUDA not available and user opted out.")
            use_cuda = False
        
        if install_pytorch_choice:
            install_pytorch(env_name, use_cuda, cuda_version)
        if install_tensorflow_choice:
            install_tensorflow(env_name, use_cuda)
    
    except Exception as e:
        log(f"Encountered exception: {e}")
        if env_created and env_name:
            remove_conda_env(env_name)
        sys.exit(1)
    
    install_requirements(env_name)
    install_additional_packages(env_name)
    os.system("conda env export --no-builds > environment.yml")
    log(f"Setup complete! Activate your environment using: conda activate {env_name}")

if __name__ == '__main__':
    main()
