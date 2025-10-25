# Python Version Compatibility Solution

## Problem Statement

The Spleeter module requires Python 3.8, while the rest of the codebase can run on Python 3.12. The challenge was to organize the files so both Python versions can coexist in one project.

## Solution: Microservice Architecture

We implemented a microservice architecture that separates the Spleeter functionality into its own service, allowing the main pipeline to use modern Python features.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Pipeline (Python 3.12+)              │
│                                                               │
│  • Whisper transcription                                     │
│  • Gemini lyric generation                                   │
│  • ElevenLabs voice synthesis                                │
│  • Audio mixing with pydub                                   │
│                                                               │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ HTTP REST API
                     │ (POST /separate)
                     │
┌────────────────────┴──────────────────────────────────────────┐
│           Spleeter Service (Python 3.8)                       │
│                                                               │
│  • Flask API server on port 5001                             │
│  • Spleeter audio separation                                 │
│  • Isolated Python 3.8 environment                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Spleeter Service (Python 3.8)

**Location:** `spleeter_service/`

**Components:**
- `app.py` - Flask REST API for audio separation
- `requirements.txt` - Python 3.8 dependencies (spleeter, flask)
- `start.sh` - Automated setup and startup script
- `README.md` - Service documentation

**API Endpoints:**
- `GET /health` - Health check
- `POST /separate` - Separate audio into vocals and instrumental

### 2. Main Pipeline (Python 3.12+)

**Components:**
- `pipeline.py` - Updated to use HTTP client instead of importing Spleeter
- `requirements-main.txt` - Python 3.12+ dependencies
- All other processing remains in main pipeline

**Key Change in `pipeline.py`:**
```python
# Before: Direct Spleeter import (Python 3.8 required)
from spleeter.separator import Separator
separator = Separator('spleeter:2stems')

# After: HTTP call to Spleeter service (any Python version)
import requests
response = requests.post(f"{service_url}/separate", json={...})
```

### 3. Developer Experience

**Convenience Scripts:**
- `run_pipeline.sh` - Auto-starts Spleeter service and runs pipeline
- `test_spleeter_service.py` - Health check for service

**Documentation:**
- `SETUP.md` - Comprehensive setup guide
- `README.md` - Updated with architecture and usage
- `spleeter_service/README.md` - Service-specific docs

## Benefits

✅ **Version Flexibility**: Main pipeline uses Python 3.12+ features
✅ **Backward Compatibility**: Spleeter runs on Python 3.8
✅ **Clean Separation**: Services can be deployed independently
✅ **Horizontal Scaling**: Spleeter service can scale separately
✅ **Easy Development**: Convenience scripts simplify workflow
✅ **Future-Proof**: Easy to add more services or update Python versions

## Usage

### Quick Start

```bash
# Automatic (recommended)
./run_pipeline.sh --song input.mp3 --theme "space exploration"
```

### Manual Control

```bash
# Terminal 1: Start Spleeter service (Python 3.8)
cd spleeter_service && ./start.sh

# Terminal 2: Run main pipeline (Python 3.12+)
python pipeline.py --song input.mp3 --theme "space exploration"
```

## Migration Path

For users upgrading from the previous monolithic setup:

1. **Old Setup (Single Python 3.8 Environment):**
   ```
   pip install -r requirements.txt
   python pipeline.py --song input.mp3 --theme "theme"
   ```

2. **New Setup (Dual Environment):**
   ```
   # Setup (one-time)
   pip install -r requirements-main.txt
   cd spleeter_service && ./start.sh
   
   # Usage
   ./run_pipeline.sh --song input.mp3 --theme "theme"
   ```

## Technical Decisions

### Why HTTP/REST instead of other IPC methods?

- **Simplicity**: Standard HTTP is well-understood and widely supported
- **Language Agnostic**: Could replace Spleeter with any language/service
- **Debugging**: Easy to test with curl or Postman
- **Deployment**: Can deploy services to different machines/containers

### Why Flask for the Spleeter service?

- **Lightweight**: Minimal overhead for simple API
- **Python Native**: Easy integration with Spleeter
- **Well-Documented**: Large community and good documentation
- **Compatible**: Works with Python 3.8

### Why separate requirements files?

- **Clarity**: Explicit about which dependencies need which Python version
- **Safety**: Prevents accidental incompatible package installations
- **Documentation**: Self-documenting which environment needs what

## Testing

All code has been validated for:
- ✅ Python syntax correctness
- ✅ Import compatibility
- ✅ Service communication protocol
- ✅ Documentation accuracy

## Future Enhancements

Possible improvements:
- Add Docker containers for even easier deployment
- Implement service discovery for multiple Spleeter instances
- Add authentication/API keys for production use
- Implement request queuing for concurrent processing
- Add monitoring and metrics collection

## Summary

This solution elegantly solves the Python version compatibility problem by:
1. Isolating incompatible dependencies into separate services
2. Using HTTP/REST for inter-service communication
3. Maintaining developer convenience with automation scripts
4. Providing comprehensive documentation for all skill levels

The result is a maintainable, scalable, and future-proof architecture that supports both Python 3.8 (Spleeter) and Python 3.12+ (main pipeline) in a single project.
