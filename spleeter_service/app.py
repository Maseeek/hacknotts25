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

# Import Spleeter (requires Python 3.8)
try:
    from spleeter.separator import Separator
    SPLEETER_AVAILABLE = True
except ImportError:
    SPLEETER_AVAILABLE = False
    print("WARNING: Spleeter not available. Install with: pip install spleeter")


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
        
        audio_path = data['audio_path']
        output_dir = data.get('output_dir', 'output/separated')
        
        # Validate input file exists
        if not os.path.exists(audio_path):
            return jsonify({
                'success': False,
                'error': f'Audio file not found: {audio_path}'
            }), 404
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Spleeter
        print(f"[Spleeter Service] Separating audio: {audio_path}")
        separator = Separator('spleeter:2stems')
        
        # Get song name
        song_name = Path(audio_path).stem
        
        # Separate the audio
        separator.separate_to_file(audio_path, str(output_path))
        
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
        
        print(f"[Spleeter Service] ✓ Vocals: {vocals_path}")
        print(f"[Spleeter Service] ✓ Instrumental: {instrumental_path}")
        
        return jsonify({
            'success': True,
            'vocals_path': str(vocals_path),
            'instrumental_path': str(instrumental_path)
        })
    
    except Exception as e:
        print(f"[Spleeter Service] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("SPLEETER MICROSERVICE")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Spleeter available: {SPLEETER_AVAILABLE}")
    print("=" * 60)
    print("\nStarting server on http://localhost:5001")
    print("Endpoints:")
    print("  GET  /health   - Health check")
    print("  POST /separate - Separate audio")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
