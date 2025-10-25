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

This project uses two Python environments to handle different dependency requirements:

### Main Pipeline (Python 3.12+)

The main pipeline, lyric generation, voice synthesis, and mixing components run on Python 3.12 or higher.

1. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements-main.txt
   ```

### Spleeter Service (Python 3.8)

Audio separation requires Python 3.8 due to Spleeter library compatibility. This runs as a separate microservice.

1. **Navigate to the service directory**:
   ```bash
   cd spleeter_service
   ```

2. **Run the setup script** (creates virtual environment and installs dependencies):
   ```bash
   ./start.sh
   ```

   Or manually:
   ```bash
   python3.8 -m venv venv38
   source venv38/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

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

```bash
python test_api_key.py
```

This will:
- Check if the `.env` file is loaded correctly
- Verify that the API key is set
- Test connectivity to the Gemini API (if a valid key is provided)

### Testing Spleeter Service

To verify the Spleeter service is set up correctly:

```bash
python test_spleeter_service.py
```

## Usage

### Option 1: Automatic (Recommended)

Use the convenience script that manages both services:

```bash
./run_pipeline.sh --song <path_to_song> --theme <theme>
```

This script will:
- Automatically start the Spleeter service if it's not running
- Run the main pipeline
- Keep the Spleeter service running for subsequent uses

### Option 2: Manual Control

**Terminal 1 - Start Spleeter Service (Python 3.8):**
```bash
cd spleeter_service
./start.sh
```

**Terminal 2 - Run Main Pipeline (Python 3.12+):**
```bash
source venv/bin/activate  # If using virtual environment
python pipeline.py --song <path_to_song> --theme <theme>
```

### Examples

```bash
# Using the convenience script (recommended)
./run_pipeline.sh --song input.mp3 --theme "space exploration"
./run_pipeline.sh --song my_song.wav --theme "medieval fantasy" --artist "Drake"

# Or manually if services are already running
python pipeline.py --song input.mp3 --theme "space exploration"
python pipeline.py --song my_song.wav --theme "medieval fantasy"
python pipeline.py --song input.mp3 --theme "space exploration" --artist "Drake"
```

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
