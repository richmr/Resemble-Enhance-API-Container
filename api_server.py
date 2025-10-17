import torch
import torchaudio
import io
import tempfile
import os
from pathlib import Path
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename

from resemble_enhance.enhancer.inference import denoise

app = Flask(__name__)

# Device configuration
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

print(f"Using device: {device}")

def _fn(path):
    """Denoise function based on the pattern from denoise_test.py"""
    if path is None:
        return None, None

    dwav, sr = torchaudio.load(path)
    # dwav = dwav.mean(dim=0)

    wav1, new_sr = denoise(dwav[0], sr, device)

    # wav1 = wav1.cpu().numpy()

    return wav1, new_sr

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "device": device})

@app.route('/denoise', methods=['POST'])
def denoise_audio():
    """Endpoint to denoise audio files"""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file extension
        if not file.filename.lower().endswith(('.wav', '.wave')):
            return jsonify({"error": "Only WAV files are supported"}), 400
        
        # Create temporary file to save uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_input:
            file.save(temp_input.name)
            temp_input_path = temp_input.name
        
        try:
            # Process the audio file using the _fn function
            denoised_audio, sample_rate = _fn(temp_input_path)
            
            if denoised_audio is None:
                return jsonify({"error": "Failed to process the audio file"}), 500
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
                # Save denoised audio
                torchaudio.save(temp_output.name, denoised_audio[None], sample_rate)
                temp_output_path = temp_output.name
            
            # Return the denoised audio file
            return send_file(
                temp_output_path,
                as_attachment=True,
                download_name=f"denoised_{secure_filename(file.filename)}",
                mimetype='audio/wav'
            )
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_input_path)
                if 'temp_output_path' in locals():
                    os.unlink(temp_output_path)
            except OSError:
                pass  # File might already be deleted
                
    except Exception as e:
        print(f"Error processing audio file: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "message": "Audio Denoiser API",
        "endpoints": {
            "/health": "GET - Health check",
            "/denoise": "POST - Upload WAV file to denoise",
            "/": "GET - This information"
        },
        "device": device
    })

if __name__ == '__main__':
    print("Starting Audio Denoiser API Server...")
    print(f"Device: {device}")
    app.run(host='0.0.0.0', port=6488, debug=False)
