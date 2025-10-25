# AI Song Pipeline - HackNotts 2025

An AI-powered song transformation pipeline that separates, transcribes, rewrites, and remixes songs with themed lyrics.

## Features

The pipeline consists of 5 specialized agents:

1. **Pre-Process Agent**: Separates vocals from instrumental using Spleeter and transcribes lyrics with timing using Whisper
2. **Lyric Generation Agent**: Rewrites lyrics to match a specified theme using Google Gemini
3. **Voice Synthesis Agent**: Placeholder for future TTS/voice cloning implementation
4. **Aligner Agent**: Placeholder for DTW-based audio alignment
5. **Mixer Agent**: Overlays processed vocals on instrumental using pydub

## Installation

### Step 1: Prerequisites

Before installing the project, ensure you have:

1. **Python 3.10 or 3.11** installed ([Download Python](https://www.python.org/downloads/))
   ```bash
   # Check your Python version
   python --version
   # or
   python3 --version
   ```

2. **FFmpeg** installed (required for audio processing)
   ```bash
   # Windows (with Chocolatey)
   choco install ffmpeg
   
   # macOS (with Homebrew)
   brew install ffmpeg
   
   # Linux (Ubuntu/Debian)
   sudo apt-get update
   sudo apt-get install ffmpeg
   
   # Verify FFmpeg installation
   ffmpeg -version
   ```

3. **Git** installed ([Download Git](https://git-scm.com/downloads))
   ```bash
   git --version
   ```

### Step 2: Clone the Repository

```bash
git clone https://github.com/Maseeek/hacknotts25.git
cd hacknotts25
```

### Step 3: Set Up Python Environment

Choose one of the following methods:

### Recommended Method (avoids building numpy from source)

```bash
# Upgrade pip, setuptools, and wheel first
python -m pip install --upgrade pip setuptools wheel

# Install numpy as a binary (avoids source builds on Windows)
python -m pip install numpy --only-binary=:all:

# Install the package in editable mode
python -m pip install -e .
```

### Alternative Method (for Conda/Anaconda users on Windows)

```bash
# Create a conda environment with numpy pre-installed
conda create -n hacknotts25 python=3.10 numpy
conda activate hacknotts25

# Install the package
pip install -e .
```

### Legacy Method (using requirements.txt)

```bash
pip install -r requirements.txt
```

**Note**: The recommended method ensures numpy is installed as a pre-built binary wheel, which is significantly faster and avoids compilation issues on Windows.

### Step 4: Configure Your IDE/Editor

#### Visual Studio Code

1. **Install Python extension**: Search for "Python" in VS Code extensions
2. **Select interpreter**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "Python: Select Interpreter"
   - Choose the Python interpreter from your virtual environment (if using venv) or your system Python 3.10/3.11

3. **Configure workspace settings** (optional `.vscode/settings.json`):
   ```json
   {
       "python.defaultInterpreterPath": "python",
       "python.terminal.activateEnvironment": true,
       "python.linting.enabled": true,
       "python.linting.pylintEnabled": false,
       "python.linting.flake8Enabled": true
   }
   ```

#### PyCharm

1. **Configure Python interpreter**:
   - Go to `File > Settings > Project > Python Interpreter`
   - Click the gear icon and select "Add Interpreter"
   - Choose "System Interpreter" and select Python 3.10/3.11
   - Or create a new virtual environment

2. **Mark directory as sources root**:
   - Right-click the project folder
   - Select "Mark Directory as" > "Sources Root"

#### Jupyter Notebook

```bash
# Install Jupyter
pip install jupyter

# Launch notebook
jupyter notebook
```

#### Command Line / Terminal

Just ensure Python is in your PATH:
```bash
# Verify Python is accessible
python --version

# Run the pipeline
python pipeline.py --song input.mp3 --theme "space exploration"
```

### Step 5: Set Up Environment Variables

Create a `.env` file in the project root (already present in repository):

```bash
# Required for lyric generation (Stage 2)
GEMINI_API_KEY=your_api_key_here
```

To get a Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### Step 6: Verify Installation

```bash
# Test that the pipeline module imports correctly
python -c "import pipeline; print('✓ Pipeline module loaded successfully')"

# Run the packaging tests
python test_packaging.py
```

## Usage

```bash
python pipeline.py --song <path_to_song> --theme <theme>
```

### Examples

```bash
# Transform a song with a space exploration theme
python pipeline.py --song input.mp3 --theme "space exploration"

# Rewrite lyrics with a medieval fantasy theme
python pipeline.py --song my_song.wav --theme "medieval fantasy"
```

### Environment Variables

- `GEMINI_API_KEY`: Required for lyric generation (Stage 2)

## System Requirements

### Python Version
- **Recommended**: Python 3.10 or 3.11
- **Minimum**: Python 3.7
- **Maximum tested**: Python 3.12

**Note**: Python 3.10-3.11 are recommended for best compatibility with audio processing libraries. Python 3.7 is minimum but some dependencies may require newer versions.

### Operating Systems
- **Windows**: Windows 10/11 (64-bit)
- **macOS**: macOS 10.14 (Mojave) or later
- **Linux**: Ubuntu 20.04+ / Debian 10+ / other modern distributions

### Additional Requirements
- **FFmpeg**: Required by Spleeter and pydub for audio processing
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg` (Ubuntu/Debian)
- **Git**: For cloning the repository
- **4GB+ RAM**: Recommended for audio processing
- **Storage**: 1GB+ free space for models and output files

## Python Dependencies

The following packages are automatically installed:
- **spleeter**: Audio source separation (vocals/instrumental)
- **openai-whisper**: Speech-to-text transcription with timestamps
- **google-generativeai**: Gemini API for lyric generation
- **librosa**: Audio analysis and processing
- **fastdtw**: Dynamic Time Warping (for future alignment features)
- **pydub**: Audio manipulation and mixing
- **numpy**: Numerical computing
- **scipy**: Scientific computing utilities

## Pipeline Stages

### Stage 1: Pre-Processing
- Separates audio into vocals and instrumental tracks using Spleeter
- Transcribes lyrics with word-level timestamps using Whisper

### Stage 2: Lyric Generation
- Uses Google Gemini to rewrite lyrics matching the specified theme
- Maintains structure and rhythm of original lyrics

### Stage 3: Voice Synthesis (Placeholder)
- Future: Will synthesize new vocals from rewritten lyrics
- Currently returns original vocals

### Stage 4: Alignment (Placeholder)
- Future: Will use Dynamic Time Warping (DTW) to align vocals
- Currently returns vocals unchanged

### Stage 5: Mixing
- Overlays processed vocals on instrumental track
- Exports final mixed audio

## Output

The pipeline creates an `output/` directory containing:
- Separated vocal and instrumental tracks
- Final mixed audio file

## Troubleshooting Setup Issues

### Python Version Issues

**Problem**: "Python version not supported"
```bash
# Check your Python version
python --version

# If too old, download Python 3.10 or 3.11 from python.org
# Make sure to check "Add Python to PATH" during installation
```

### FFmpeg Not Found

**Problem**: "ffmpeg not found" or "FileNotFoundError: ffmpeg"
```bash
# Verify FFmpeg is installed and in PATH
ffmpeg -version

# If not found, install FFmpeg (see Prerequisites section)
# On Windows, you may need to add FFmpeg to your system PATH manually
```

### NumPy Build Issues (Windows)

**Problem**: "Building wheel for numpy" taking too long or failing
```bash
# Solution: Use the recommended installation method with binary-only numpy
python -m pip install --upgrade pip setuptools wheel
python -m pip install numpy --only-binary=:all:
python -m pip install -e .
```

### Import Errors

**Problem**: "ModuleNotFoundError" for dependencies
```bash
# Ensure you're in the project directory
cd hacknotts25

# Reinstall dependencies
pip install -e .

# Or use requirements.txt
pip install -r requirements.txt
```

### Gemini API Key Issues

**Problem**: "No Gemini API key found" or Stage 2 fails
```bash
# Check your .env file exists and contains:
# GEMINI_API_KEY=your_actual_key_here

# Verify the key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('GEMINI_API_KEY')[:10] + '...' if os.getenv('GEMINI_API_KEY') else 'NOT FOUND')"
```

### Permission Errors

**Problem**: Permission denied when installing packages
```bash
# Linux/macOS: Don't use sudo with pip
# Instead, use a virtual environment or user installation:
pip install --user -r requirements.txt

# Or create a virtual environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## License

MIT