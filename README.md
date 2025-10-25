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

```bash
pip install -r requirements.txt
```

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

## Usage

**Note**: Audio separation (Spleeter) is not available in Python 3.12. You must provide pre-separated vocals and instrumental files.

```bash
python pipeline.py --vocals <vocals.wav> --instrumental <instrumental.wav> --theme <theme>
```

### Examples

```bash
# Transform pre-separated audio with a space exploration theme
python pipeline.py --vocals vocals.wav --instrumental instrumental.wav --theme "space exploration"

# Rewrite lyrics with a medieval fantasy theme and specific artist voice style
python pipeline.py --vocals vocals.wav --instrumental instrumental.wav --theme "medieval fantasy" --artist "Drake"
```

### Environment Variables

- `GEMINI_API_KEY`: Required for lyric generation (Stage 2)
- `ELEVENLABS_API_KEY`: Required for voice synthesis (Stage 3)

## Requirements

- Python 3.12+ (upgraded from 3.8)
- Dependencies listed in `requirements.txt`:
  - openai-whisper (speech-to-text)
  - google-generativeai >=0.3.0 (lyric generation with Gemini)
  - librosa (audio processing)
  - fastdtw (for future alignment)
  - pydub (audio mixing)
  - numpy, scipy (numerical processing)
  - python-dotenv (environment variable loading)

### Note on Audio Separation

**Spleeter has been removed** from this project as it requires Python 3.8 and is not compatible with Python 3.12.

If you need audio separation (vocals from instrumental), you have two options:

1. **Use a separate Python 3.8 environment**: Create a dedicated Python 3.8 environment, install Spleeter there, and run audio separation separately
2. **Use pre-separated audio files**: If you already have separated vocal and instrumental tracks, you can provide them directly to the pipeline

The rest of the pipeline (lyric generation, voice synthesis, mixing, etc.) now runs on Python 3.12.

## Pipeline Stages

### Stage 1: Pre-Processing
- **Audio separation has been removed** (Spleeter requires Python 3.8)
  - Option 1: Use pre-separated vocal and instrumental tracks
  - Option 2: Run Spleeter in a separate Python 3.8 environment
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
