FROM ubuntu:22.04

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    wget \
    git \
    python3-dev \
    python3-pip \
    libgl1-mesa-glx \
    libsdl2-dev \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.8
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3.8-distutils && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    update-alternatives --config python3

# Create a working directory
WORKDIR /app

#RUN pip3 install setuptools distutils

# Copy the requirements file
COPY requirements.txt .
COPY autopilot.py .

# Install Python dependencies
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
# Copy the application code
COPY script.py .

# Set the default command to run when the container starts
CMD ["script.py"]