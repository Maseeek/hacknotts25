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

- Python 3.7+
- Dependencies listed in `requirements.txt`:
  - spleeter (audio separation)
  - openai-whisper (speech-to-text)
  - google-generativeai (lyric generation with Gemini)
  - librosa (audio processing)
  - fastdtw (for future alignment)
  - pydub (audio mixing)
  - numpy, scipy (numerical processing)

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