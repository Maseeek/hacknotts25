# Spleeter Microservice

This service provides audio separation functionality using Spleeter, which requires Python 3.8.

## Requirements

- Python 3.8 (required for Spleeter compatibility)
- See `requirements.txt` for Python dependencies

## Setup

1. **Install Python 3.8** (if not already installed):
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install python3.8 python3.8-venv
   
   # On macOS with Homebrew
   brew install python@3.8
   ```

2. **Create a Python 3.8 virtual environment**:
   ```bash
   python3.8 -m venv venv38
   source venv38/bin/activate  # On Windows: venv38\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Service

```bash
# Activate the Python 3.8 environment
source venv38/bin/activate

# Start the service
python app.py
```

The service will start on `http://localhost:5001`

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "spleeter_available": true,
  "python_version": "3.8.x"
}
```

### Separate Audio
```bash
POST /separate
Content-Type: application/json

{
  "audio_path": "/absolute/path/to/audio.mp3",
  "output_dir": "/absolute/path/to/output"
}
```

Response:
```json
{
  "success": true,
  "vocals_path": "/path/to/vocals.wav",
  "instrumental_path": "/path/to/accompaniment.wav"
}
```

## Testing

```bash
# Check service is running
curl http://localhost:5001/health

# Test audio separation
curl -X POST http://localhost:5001/separate \
  -H "Content-Type: application/json" \
  -d '{"audio_path": "/path/to/song.mp3", "output_dir": "/path/to/output"}'
```

## Notes

- The service must be running for the main pipeline to work
- All paths should be absolute paths
- Large audio files may take several minutes to process
- The service binds to `0.0.0.0:5001` by default
