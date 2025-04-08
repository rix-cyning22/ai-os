Code to generate a docker image of AI-optimised OS.

# Functionalities:
1. The OS comes pre-installed with CUDA for NVIDIA GPU support, miniconda for version management and virtual environment creation, pytorch and tensorflow.
2. A smart scheduling algorithm has been built that can schedule processes using an ML algorithm
3. A smart anomaly detection algorithm that can flag anomalous processes that consume too much memory or takes too long to execute.
4. A CLI-based resource monitoring program
5. GUI support for resource monitoring program. A dashboard visualises the resources being used
6. a script to automate virtual environment set up using conda
7. An installation script (ONLY USE IT IF DOCKER IS NOT ALREADY INSTALLED!!)
8. GPU memory management scripts