# Audio Denoiser API

A containerized audio denoising service built with Flask and PyTorch, powered by the [Resemble Enhance model](https://github.com/resemble-ai/resemble-enhance). This service provides a REST API for denoising audio files using state-of-the-art AI models.

## Features

- **AI-Powered Denoising**: Uses Resemble Enhance models for high-quality audio denoising
- **REST API**: Simple HTTP endpoints for easy integration
- **Containerized**: Docker-based deployment for consistent environments
- **GPU Support**: Automatic CUDA detection and utilization when available
- **File Format Support**: Accepts WAV audio files
- **Health Monitoring**: Built-in health check endpoint

## Building the Container

### Prerequisites

- Docker installed on your system
- Git LFS support (for model downloads)

### Build Process

1. **Navigate to the denoiser directory:**
   ```bash
   cd denoiser
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t audio-denoiser .
   ```

   This will:
   - Pull the PyTorch CUDA runtime base image
   - Install Git LFS for model downloads
   - Install Python dependencies from `requirements.txt`
   - Clone the Resemble Enhance model repository
   - Set up the Flask API server

3. **Verify the build:**
   ```bash
   docker images | grep audio-denoiser
   ```

### Container Configuration

The container is configured with:
- **Base Image**: `pytorch/pytorch:2.1.1-cuda12.1-cudnn8-runtime`
- **Port**: 6488 (exposed)
- **Working Directory**: `/app`
- **Model Repository**: Automatically cloned from Hugging Face

## Running the Container

### Basic Usage

```bash
docker run -p 6488:6488 audio-denoiser
```

### With GPU Support

```bash
docker run --gpus all -p 6488:6488 audio-denoiser
```

### Background Mode

```bash
docker run -d --name denoiser-api -p 6488:6488 audio-denoiser
```

### Check Container Status

```bash
# View logs
docker logs denoiser-api

# Check if running
docker ps | grep denoiser-api
```

## API Usage

### Base URL
```
http://localhost:6488
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "device": "cuda"
}
```

#### 2. API Information
```http
GET /
```

**Response:**
```json
{
  "message": "Audio Denoiser API",
  "endpoints": {
    "/health": "GET - Health check",
    "/denoise": "POST - Upload WAV file to denoise",
    "/": "GET - This information"
  },
  "device": "cuda"
}
```

#### 3. Denoise Audio
```http
POST /denoise
Content-Type: multipart/form-data
```

**Request:**
- Method: POST
- Content-Type: `multipart/form-data`
- Body: WAV file in `file` field

**Response:**
- Content-Type: `audio/wav`
- File: Denoised audio file (downloadable)

**Error Responses:**
- `400`: No file provided, no file selected, or unsupported file format
- `500`: Processing error or internal server error

## Sample Code

### Python Example

```python
import requests
import os

def denoise_audio(file_path, api_url="http://localhost:6488"):
    """
    Denoise an audio file using the API
    
    Args:
        file_path (str): Path to the input WAV file
        api_url (str): Base URL of the denoiser API
    
    Returns:
        bytes: Denoised audio data
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Prepare the file for upload
    with open(file_path, 'rb') as audio_file:
        files = {'file': (os.path.basename(file_path), audio_file, 'audio/wav')}
        
        # Make the request
        response = requests.post(f"{api_url}/denoise", files=files)
    
    # Check for errors
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

# Example usage
if __name__ == "__main__":
    try:
        # Denoise an audio file
        input_file = "noisy_audio.wav"
        denoised_data = denoise_audio(input_file)
        
        # Save the result
        with open("denoised_audio.wav", "wb") as f:
            f.write(denoised_data)
        
        print("Audio denoised successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
```

### cURL Example

```bash
# Health check
curl -X GET http://localhost:6488/health

# Denoise audio file
curl -X POST \
  -F "file=@noisy_audio.wav" \
  -o denoised_audio.wav \
  http://localhost:6488/denoise
```


## Development and Testing

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python api_server.py
   ```

3. **Test with sample file:**
   ```bash
   curl -X POST -F "file=@test_in/noisy_privet.wav" -o test_output.wav http://localhost:6488/denoise
   ```

### Testing the API

```python
import requests

# Test health endpoint
response = requests.get("http://localhost:6488/health")
print("Health check:", response.json())

# Test denoise endpoint
with open("test_in/noisy_privet.wav", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:6488/denoise", files=files)
    
if response.status_code == 200:
    with open("test_output.wav", "wb") as f:
        f.write(response.content)
    print("Denoising successful!")
else:
    print("Error:", response.text)
```

## Requirements

- **Python**: 3.10+
- **PyTorch**: 2.1.1+
- **TorchAudio**: 2.1.1+
- **Flask**: 2.0.0+
- **Resemble Enhance**: Latest version
- **Docker**: For containerized deployment
- **CUDA**: Optional, for GPU acceleration

## Troubleshooting

### Common Issues

1. **"No file provided" error:**
   - Ensure you're sending the file in the `file` field
   - Check that the file is actually selected/uploaded

2. **"Only WAV files are supported" error:**
   - Convert your audio file to WAV format
   - Ensure the file extension is `.wav` or `.wave`

3. **CUDA out of memory:**
   - The model requires significant GPU memory
   - Consider using CPU mode or a GPU with more memory
   - Reduce audio file length if possible

4. **Model download issues:**
   - Ensure Git LFS is installed
   - Check internet connectivity
   - Verify Hugging Face access

### Performance Tips

- Use GPU when available for faster processing
- Keep audio files reasonably sized (< 10 minutes)
- Consider batch processing for multiple files
- Monitor memory usage during processing

## License

This project uses the Resemble Enhance model. Please refer to the original [Resemble Enhance repository](https://github.com/resemble-ai/resemble-enhance) for licensing information.
