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

> 📖 **For detailed setup instructions, see [SETUP.md](SETUP.md)**

This project uses two Python environments to handle different dependency requirements.

### Prerequisites

**All Platforms:**
- Python 3.8 (for Spleeter service)
- Python 3.12+ (for main pipeline)
- Git

**Windows Users:**
- Download and install Python 3.8 from [python.org](https://www.python.org/downloads/release/python-3810/)
- Download and install Python 3.12 from [python.org](https://www.python.org/downloads/)
- Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) and add to PATH

---

### Quick Setup

<details>
<summary><b>Windows</b></summary>

#### 1. Main Pipeline (Python 3.12+)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements-main.txt
```

#### 2. Spleeter Service (Python 3.8)

```powershell
# Navigate to service directory
cd spleeter_service

# Create Python 3.8 virtual environment
py -3.8 -m venv venv38

# Activate it
venv38\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Return to project root
cd ..
```

#### 3. Configure API Keys

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your-actual-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

</details>

<details>
<summary><b>Linux / macOS</b></summary>

#### 1. Main Pipeline (Python 3.12+)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements-main.txt
```

#### 2. Spleeter Service (Python 3.8)

```bash
# Navigate to service directory
cd spleeter_service

# Run the automated setup script
./start.sh
```

Or manually:
```bash
python3.8 -m venv venv38
source venv38/bin/activate
pip install -r requirements.txt
cd ..
```

#### 3. Configure API Keys

Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your-actual-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

</details>

See [`spleeter_service/README.md`](spleeter_service/README.md) for detailed setup instructions.

## Setup

### API Key Configuration

The pipeline requires a Google Gemini API key for lyric generation (Stage 2).

1. Create a `.env` file in the project root (if it doesn't exist)
2. Add your Gemini API key:
   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```

### Testing Your API Key

To verify that your API key is properly configured, run the test script:

**Windows:**
```powershell
venv\Scripts\activate
python test_api_key.py
```

**Linux/macOS:**
```bash
source venv/bin/activate
python test_api_key.py
```

This will:
- Check if the `.env` file is loaded correctly
- Verify that the API key is set
- Test connectivity to the Gemini API (if a valid key is provided)

### Testing Spleeter Service

To verify the Spleeter service is set up correctly:

**Windows:**
```powershell
venv\Scripts\activate
python test_spleeter_service.py
```

**Linux/macOS:**
```bash
source venv/bin/activate
python test_spleeter_service.py
```

## Usage

### Running the Pipeline

<details>
<summary><b>Windows</b></summary>

#### Option 1: All-in-One (Recommended for Testing)

**Terminal 1 - Start Spleeter Service:**
```powershell
# Activate Spleeter environment
cd spleeter_service
venv38\Scripts\activate

# Start the service
python app.py
```

**Terminal 2 - Run Main Pipeline:**
```powershell
# Activate main environment
venv\Scripts\activate

# Run the pipeline
python pipeline.py --song path\to\song.mp3 --theme "space exploration"
```

#### Option 2: Quick Test (if Spleeter service is already running)

```powershell
# Activate main environment
venv\Scripts\activate

# Test service is running
python test_spleeter_service.py

# Run pipeline
python pipeline.py --song input.mp3 --theme "your theme"
```

#### Examples

```powershell
# Basic usage
python pipeline.py --song input.mp3 --theme "space exploration"

# With artist voice style
python pipeline.py --song my_song.wav --theme "medieval fantasy" --artist "Drake"
```

</details>

<details>
<summary><b>Linux / macOS</b></summary>

#### Option 1: Automatic (Recommended)

Use the convenience script that manages both services:

```bash
./run_pipeline.sh --song <path_to_song> --theme <theme>
```

This script will:
- Automatically start the Spleeter service if it's not running
- Run the main pipeline
- Keep the Spleeter service running for subsequent uses

#### Option 2: Manual Control

**Terminal 1 - Start Spleeter Service:**
```bash
cd spleeter_service
./start.sh
```

**Terminal 2 - Run Main Pipeline:**
```bash
source venv/bin/activate
python pipeline.py --song <path_to_song> --theme <theme>
```

#### Examples

```bash
# Using the convenience script
./run_pipeline.sh --song input.mp3 --theme "space exploration"
./run_pipeline.sh --song my_song.wav --theme "medieval fantasy" --artist "Drake"

# Or manually if services are already running
python pipeline.py --song input.mp3 --theme "space exploration"
```

</details>

### Environment Variables

- `GEMINI_API_KEY`: Required for lyric generation (Stage 2)
- `ELEVENLABS_API_KEY`: Optional for voice synthesis (Stage 3)

## Architecture

The project uses a microservice architecture to support different Python versions:

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Pipeline (Python 3.12+)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Whisper     │  │   Gemini     │  │ ElevenLabs   │      │
│  │ Transcription│  │Lyric Rewrite │  │Voice Synthesis│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │     DTW      │  │    Pydub     │                        │
│  │  Alignment   │  │    Mixing    │                        │
│  └──────────────┘  └──────────────┘                        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
                     │ (localhost:5001)
┌────────────────────┴────────────────────────────────────────┐
│           Spleeter Service (Python 3.8)                      │
│  ┌──────────────────────────────────────┐                   │
│  │  Spleeter Audio Separation (2-stems) │                   │
│  │  Vocals + Instrumental               │                   │
│  └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**

- **Main Pipeline (Python 3.12+)**: Handles transcription, lyric generation, voice synthesis, and mixing
- **Spleeter Service (Python 3.8)**: Isolated microservice for audio separation via REST API on port 5001

This separation allows:
- ✅ Using modern Python features in the main pipeline
- ✅ Maintaining compatibility with Spleeter's Python 3.8 requirement
- ✅ Easy deployment and scaling of individual components

## Requirements

### Main Pipeline (Python 3.12+)
- Dependencies in `requirements-main.txt`:
  - openai-whisper (speech-to-text)
  - google-generativeai >=0.3.0 (lyric generation with Gemini)
  - elevenlabs (voice synthesis)
  - librosa (audio processing)
  - fastdtw (for future alignment)
  - pydub (audio mixing)
  - numpy, scipy (numerical processing)
  - python-dotenv (environment variable loading)
  - requests (API communication)

### Spleeter Service (Python 3.8)
- Dependencies in `spleeter_service/requirements.txt`:
  - spleeter (audio separation)
  - flask (REST API server)

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

## License

MIT
