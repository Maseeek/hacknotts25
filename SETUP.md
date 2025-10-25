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
- Install Python 3.8 from [python.org](https://www.python.org/downloads/release/python-3810/)
  - ⚠️ **Important**: Check "Add Python to PATH" during installation
  - Note the installation directory (e.g., `C:\Users\YourName\AppData\Local\Programs\Python\Python38`)
- Install Python 3.12 from [python.org](https://www.python.org/downloads/)
  - ⚠️ **Important**: Check "Add Python to PATH" during installation
- Install FFmpeg:
  - Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
  - Extract to a directory (e.g., `C:\ffmpeg`)
  - Add `C:\ffmpeg\bin` to your system PATH
  - Verify with: `ffmpeg -version` in a new terminal

## Step 1: Clone the Repository

**Linux/macOS:**
```bash
git clone https://github.com/Maseeek/hacknotts25.git
cd hacknotts25
```

**Windows (PowerShell or Command Prompt):**
```powershell
git clone https://github.com/Maseeek/hacknotts25.git
cd hacknotts25
```

## Step 2: Set Up Main Pipeline (Python 3.12+)

**Linux/macOS:**
```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-main.txt
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-main.txt
```

**Windows Note:** If you have multiple Python versions, you may need to use `py -3.12 -m venv venv` instead.

## Step 3: Set Up Spleeter Service (Python 3.8)

**Linux/macOS:**
```bash
# Navigate to service directory
cd spleeter_service

# Create Python 3.8 virtual environment
python3.8 -m venv venv38

# Activate it
source venv38/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Return to root
cd ..
```

**Windows (PowerShell):**
```powershell
# Navigate to service directory
cd spleeter_service

# Create Python 3.8 virtual environment
py -3.8 -m venv venv38

# Activate it
venv38\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Return to root
cd ..
```

**Windows Note:** If `py -3.8` doesn't work, use the full path to Python 3.8, for example:
```powershell
C:\Users\YourName\AppData\Local\Programs\Python\Python38\python.exe -m venv venv38
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

**Linux/macOS:**
```bash
# Make sure main environment is activated
source venv/bin/activate

# Use the convenience script (auto-starts Spleeter service)
./run_pipeline.sh --song path/to/song.mp3 --theme "space exploration"
```

**Windows:**

Since the bash script won't work on Windows, you need to start services manually:

**Terminal 1 - Start Spleeter Service:**
```powershell
cd spleeter_service
venv38\Scripts\activate
python app.py
```

**Terminal 2 - Run Main Pipeline:**
```powershell
venv\Scripts\activate
python pipeline.py --song path\to\song.mp3 --theme "space exploration"
```

### Manual Start (All Platforms)

**Terminal 1 - Spleeter Service:**

Linux/macOS:
```bash
cd spleeter_service
./start.sh
```

Windows:
```powershell
cd spleeter_service
venv38\Scripts\activate
python app.py
```

**Terminal 2 - Main Pipeline:**

Linux/macOS:
```bash
source venv/bin/activate
python pipeline.py --song path/to/song.mp3 --theme "your theme"
```

Windows:
```powershell
venv\Scripts\activate
python pipeline.py --song path\to\song.mp3 --theme "your theme"
```

## Troubleshooting

### "Spleeter service not available"

**Linux/macOS:**
```bash
cd spleeter_service
./start.sh
```

**Windows:**
```powershell
cd spleeter_service
venv38\Scripts\activate
python app.py
```

Check if it's responding:

Linux/macOS:
```bash
curl http://localhost:5001/health
```

Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri http://localhost:5001/health
# Or use: curl http://localhost:5001/health (if curl is available)
```

### "Module not found" errors

Make sure you're in the correct virtual environment:

**Linux/macOS:**
- Main pipeline: `source venv/bin/activate`
- Spleeter service: `source spleeter_service/venv38/bin/activate`

**Windows:**
- Main pipeline: `venv\Scripts\activate`
- Spleeter service: `spleeter_service\venv38\Scripts\activate`

### Python version errors

**Linux/macOS:**
```bash
python3.8 --version  # Should show 3.8.x
python3.12 --version # Should show 3.12.x
```

**Windows:**
```powershell
py -3.8 --version   # Should show 3.8.x
py -3.12 --version  # Should show 3.12.x
# Or use: python --version (shows default version)
```

### Windows-Specific Issues

**"py is not recognized":**
- Python launcher may not be installed. Use full path to Python executable:
  ```powershell
  C:\Users\YourName\AppData\Local\Programs\Python\Python38\python.exe --version
  ```

**"Scripts\activate is not digitally signed":**
- Run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

**FFmpeg not found:**
- Verify FFmpeg is in PATH:
  ```powershell
  ffmpeg -version
  ```
- If not found, add FFmpeg bin directory to your system PATH and restart terminal

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
