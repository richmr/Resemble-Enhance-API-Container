FROM pytorch/pytorch:2.1.1-cuda12.1-cudnn8-runtime

# the resemble-enhance download script uses `git lfs pull` to
# download the model from huggingface, which will fail unless 
# this is installed.
RUN apt update && apt install -y git-lfs

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the API server
COPY api_server.py .

# Clone the resemble-enhance model repository
RUN mkdir -p /opt/conda/lib/python3.10/site-packages/resemble_enhance/model_repo
RUN git clone https://huggingface.co/ResembleAI/resemble-enhance /opt/conda/lib/python3.10/site-packages/resemble_enhance/model_repo

# Expose the port

EXPOSE 6488

# Run the API server
CMD ["python", "api_server.py"]
