# Complete Setup Guide

This guide walks through setting up the AI Song Pipeline with its dual Python environment architecture.

## Prerequisites

- Python 3.8 (for Spleeter service)
- Python 3.12+ (for main pipeline)
- Git
- Audio processing system libraries (for pydub and librosa)

### Installing System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3.8 python3.8-venv python3.12 python3.12-venv
sudo apt-get install -y ffmpeg libsndfile1
```

**macOS:**
```bash
brew install python@3.8 python@3.12 ffmpeg libsndfile
```

**Windows:**
- Install Python 3.8 from [python.org](https://www.python.org/downloads/)
- Install Python 3.12 from [python.org](https://www.python.org/downloads/)
- Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)

## Step 1: Clone the Repository

```bash
git clone https://github.com/Maseeek/hacknotts25.git
cd hacknotts25
```

## Step 2: Set Up Main Pipeline (Python 3.12+)

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements-main.txt
```

## Step 3: Set Up Spleeter Service (Python 3.8)

```bash
# Navigate to service directory
cd spleeter_service

# Create Python 3.8 virtual environment
python3.8 -m venv venv38

# Activate it
source venv38/bin/activate  # Linux/macOS
# or
venv38\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Return to root
cd ..
```

## Step 4: Configure API Keys

Create a `.env` file in the project root:

```bash
# Required for lyric generation
GEMINI_API_KEY=your-gemini-api-key-here

# Optional for voice synthesis
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

To get API keys:
- **Gemini**: https://makersuite.google.com/app/apikey
- **ElevenLabs**: https://elevenlabs.io/app/settings/api-keys

## Step 5: Verify Setup

### Test Main Pipeline Dependencies

```bash
# Activate main pipeline environment
source venv/bin/activate

# Test API keys
python test_api_key.py

# Test imports
python -c "import whisper; import google.generativeai; print('✓ Main dependencies OK')"
```

### Test Spleeter Service

**Terminal 1 - Start the service:**
```bash
cd spleeter_service
./start.sh
```

**Terminal 2 - Test the service:**
```bash
# Activate main environment
source venv/bin/activate

# Run health check
python test_spleeter_service.py
```

If you see "✓ All checks passed!", you're ready to go!

## Running the Pipeline

### Quick Start (Recommended)

```bash
# Make sure main environment is activated
source venv/bin/activate

# Use the convenience script (auto-starts Spleeter service)
./run_pipeline.sh --song path/to/song.mp3 --theme "space exploration"
```

### Manual Start

**Terminal 1 - Spleeter Service:**
```bash
cd spleeter_service
./start.sh
```

**Terminal 2 - Main Pipeline:**
```bash
source venv/bin/activate
python pipeline.py --song path/to/song.mp3 --theme "your theme"
```

## Troubleshooting

### "Spleeter service not available"

Make sure the Spleeter service is running:
```bash
cd spleeter_service
./start.sh
```

Check if it's responding:
```bash
curl http://localhost:5001/health
```

### "Module not found" errors

Make sure you're in the correct virtual environment:
- Main pipeline: `source venv/bin/activate`
- Spleeter service: `source spleeter_service/venv38/bin/activate`

### Python version errors

Check your Python versions:
```bash
python3.8 --version  # Should show 3.8.x
python3.12 --version # Should show 3.12.x
```

### Port already in use

If port 5001 is already in use, you can:
1. Stop the process using port 5001
2. Or modify the port in `spleeter_service/app.py` and update the URL in `pipeline.py`

## Development Tips

### Running Tests

```bash
# Test API connectivity
python test_api_key.py

# Test Spleeter service
python test_spleeter_service.py

# Test voice synthesis (if ElevenLabs configured)
python test_voice_synth.py "Drake" "Test lyrics"
```

### Viewing Service Logs

```bash
# If using the convenience script
tail -f /tmp/spleeter_service.log
```

### Stopping Services

```bash
# Find and stop Spleeter service
ps aux | grep "spleeter_service"
kill <PID>

# Or restart it
cd spleeter_service
./start.sh
```

## Architecture Overview

```
Main Pipeline (Python 3.12+)    →  HTTP/REST  →  Spleeter Service (Python 3.8)
├── Whisper (transcription)                      └── Spleeter (separation)
├── Gemini (lyric generation)                        └── Flask API
├── ElevenLabs (voice synthesis)
├── DTW (alignment - placeholder)
└── Pydub (mixing)
```

## Next Steps

1. Try the example songs
2. Experiment with different themes
3. Add artist voice styles with `--artist` flag
4. Check the output in the `output/` directory

For more details, see the main [README.md](README.md).
