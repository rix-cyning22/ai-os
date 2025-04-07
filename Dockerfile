# Use the base image
FROM nycticoracs/pop_os

# Install system dependencies
RUN sudo apt-get update && sudo apt-get install -y \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libx11-xcb1 \
    libxcb1 \
    libxcb-glx0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libnss3 \
    libxss1 && \
    sudo apt-get clean
    
# Install CUDA 11.7
RUN curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub | gpg --dearmor -o /usr/share/keyrings/cuda-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cuda-archive-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" \
    > /etc/apt/sources.list.d/cuda.list && \
    apt-get update && \
    apt-get install -y cuda-toolkit-11-7 && \
    sudo apt-get clean

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm -f /tmp/miniconda.sh && \
    /opt/conda/bin/conda init && \
    /opt/conda/bin/conda update -y conda && \
    ln -s /opt/conda/bin/conda /usr/local/bin/conda

# Set up conda environment with Python 3.7 and store the environment name in OSENV
RUN /opt/conda/bin/conda create -n myenv python=3.7 -y
ENV OSENV=myenv

# Set PATH for conda environment
ENV PATH /opt/conda/envs/myenv/bin:$PATH

# Set CUDA environment variables
ENV PATH=/usr/local/cuda-11.7/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda-11.7/lib64:$LD_LIBRARY_PATH

# Install Python packages including PyQt5 and PyQtWebEngine
RUN pip install --no-cache-dir \
    scikit-learn \
    pandas \
    pypickle \
    fastapi \
    psutil \
    gputil \
    uvicorn \
    tensorflow \
    matplotlib \
    argparse \
    PyQt5 \
    PyQtWebEngine && \
    pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117

# Set working directory
WORKDIR /opt/myos

# Copy the new project structure into the container
COPY . .

# Make the shell scripts executable
RUN sudo chmod +x anomaly/app.sh && \
    sudo chmod +x dashboard/app.sh && \
    sudo chmod +x resource-monitor/app.sh && \
    sudo chmod +x scheduler/app.sh && \
    sudo chmod +x setup_env/app.sh

# Optionally, add aliases and ensure the virtual environment is activated on shell start
RUN echo "source /opt/conda/bin/activate \$OSENV" >> ~/.bashrc && \
    echo "alias anomaly='/opt/myos/anomaly/app.sh'" >> ~/.bashrc && \
    echo "alias dashboard='/opt/myos/dashboard/app.sh'" >> ~/.bashrc && \
    echo "alias resource_monitor='/opt/myos/resource-monitor/app.sh'" >> ~/.bashrc && \
    echo "alias process_scheduler='/opt/myos/scheduler/app.sh'" >> ~/.bashrc && \
    echo "alias setup_env='/opt/myos/setup_env/app.sh'" >> ~/.bashrc

# Default command to run bash
CMD ["/bin/bash"]