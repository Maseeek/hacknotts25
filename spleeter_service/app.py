#!/usr/bin/env python3
"""
Spleeter Microservice
Runs on Python 3.8 to support Spleeter library
Provides a REST API for audio separation
"""

from flask import Flask, request, jsonify
from pathlib import Path
import tempfile
import shutil
import os
import sys

app = Flask(__name__)

# Configuration
DEBUG_MODE = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}

# Import Spleeter (requires Python 3.8)
try:
    from spleeter.separator import Separator
    SPLEETER_AVAILABLE = True
except ImportError:
    SPLEETER_AVAILABLE = False
    print("WARNING: Spleeter not available. Install with: pip install spleeter")


def validate_audio_path(path_str):
    """
    Validate and sanitize audio file path to prevent path injection attacks
    Returns (is_valid, error_message, sanitized_path)
    """
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(path_str).resolve()
        
        # Check if file exists
        if not path.exists():
            return False, "File not found", None
        
        # Check if it's a file (not directory)
        if not path.is_file():
            return False, "Path must be a file", None
        
        # Check file extension
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}", None
        
        # Check file size (max 500MB)
        if path.stat().st_size > 500 * 1024 * 1024:
            return False, "File too large (max 500MB)", None
        
        return True, None, path
        
    except Exception as e:
        return False, f"Invalid path: {str(e)}", None


def validate_output_path(path_str):
    """
    Validate and sanitize output directory path
    Returns (is_valid, error_message, sanitized_path)
    """
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(path_str).resolve()
        
        # Ensure it's a valid directory path (not file)
        if path.exists() and path.is_file():
            return False, "Output path must be a directory", None
        
        return True, None, path
        
    except Exception as e:
        return False, f"Invalid output path: {str(e)}", None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'spleeter_available': SPLEETER_AVAILABLE,
        'python_version': sys.version
    })


@app.route('/separate', methods=['POST'])
def separate_audio():
    """
    Separate audio into vocals and instrumental
    
    Expected JSON payload:
    {
        "audio_path": "/path/to/audio.mp3",
        "output_dir": "/path/to/output"
    }
    
    Returns:
    {
        "success": true,
        "vocals_path": "/path/to/vocals.wav",
        "instrumental_path": "/path/to/accompaniment.wav"
    }
    """
    if not SPLEETER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Spleeter is not available. Please install it in a Python 3.8 environment.'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'audio_path' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: audio_path'
            }), 400
        
        # Validate and sanitize input path
        is_valid, error_msg, audio_path = validate_audio_path(data['audio_path'])
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Validate and sanitize output path
        output_dir_str = data.get('output_dir', 'output/separated')
        is_valid, error_msg, output_path = validate_output_path(output_dir_str)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Spleeter
        print(f"[Spleeter Service] Separating audio: {audio_path.name}")
        separator = Separator('spleeter:2stems')
        
        # Get song name
        song_name = audio_path.stem
        
        # Separate the audio
        separator.separate_to_file(str(audio_path), str(output_path))
        
        # Construct paths to separated files
        separated_dir = output_path / song_name
        vocals_path = separated_dir / "vocals.wav"
        instrumental_path = separated_dir / "accompaniment.wav"
        
        # Verify files were created
        if not vocals_path.exists() or not instrumental_path.exists():
            return jsonify({
                'success': False,
                'error': 'Separation completed but output files not found'
            }), 500
        
        print(f"[Spleeter Service] ✓ Vocals: {vocals_path.name}")
        print(f"[Spleeter Service] ✓ Instrumental: {instrumental_path.name}")
        
        return jsonify({
            'success': True,
            'vocals_path': str(vocals_path),
            'instrumental_path': str(instrumental_path)
        })
    
    except Exception as e:
        print(f"[Spleeter Service] ✗ Error: {type(e).__name__}")
        # Log full error server-side but don't expose to client
        import traceback
        traceback.print_exc()
        
        # Return generic error message to client
        return jsonify({
            'success': False,
            'error': 'An error occurred during audio separation. Check server logs for details.'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("SPLEETER MICROSERVICE")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Spleeter available: {SPLEETER_AVAILABLE}")
    print(f"Debug mode: {DEBUG_MODE}")
    print("=" * 60)
    print("\nStarting server on http://localhost:5001")
    print("Endpoints:")
    print("  GET  /health   - Health check")
    print("  POST /separate - Separate audio")
    if DEBUG_MODE:
        print("\n⚠️  WARNING: Running in DEBUG mode!")
        print("   Set FLASK_DEBUG=false for production")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=DEBUG_MODE)
