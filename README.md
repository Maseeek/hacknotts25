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

## Requirements

- Python 3.7+ (currently running 3.8 due to issues with spleeter module on higher versions)
- Dependencies listed in `requirements.txt`:
  - spleeter (audio separation)
  - openai-whisper (speech-to-text)
  - google-generativeai (lyric generation with Gemini)
  - librosa (audio processing)
  - fastdtw (for future alignment)
  - pydub (audio mixing)
  - numpy, scipy (numerical processing)
  - python-dotenv (environment variable loading)

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
