#!/usr/bin/env python3
"""
AI Song Pipeline - Transforms songs with AI-generated lyrics
"""

import argparse
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
import whisper
import librosa
import soundfile as sf
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import json
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()


# =====================================================
# 1️⃣ PRE-PROCESS AGENT
# =====================================================
class PreProcessAgent:
    """
    Handles audio preprocessing:
    - Uses Flask Spleeter microservice for vocal separation
    - Uses OpenAI Whisper for lyric transcription with timestamps
    """

    def __init__(self, spleeter_service_url="http://127.0.0.1:5001/split"):
        self.spleeter_service_url = spleeter_service_url
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def separate_audio(self, song_path):
        print("[Pre-Process Agent] Requesting audio separation from Spleeter service...")

        try:
            with open(song_path, "rb") as f:
                # Use a specific filename for the request
                files = {"file": (Path(song_path).name, f, "audio/mpeg")}
                response = requests.post(self.spleeter_service_url, files=files)

            if response.status_code != 200:
                raise Exception(f"Spleeter service error {response.status_code}: {response.text}")

            data = response.json()
            vocals_path = data.get("vocals_path")
            instrumental_path = data.get("instrumental_path")

            if not vocals_path or not instrumental_path:
                raise Exception("Spleeter service returned incomplete response")

            print(f"  ✓ Vocals saved to: {vocals_path}")
            print(f"  ✓ Instrumental saved to: {instrumental_path}")
            return vocals_path, instrumental_path

        except Exception as e:
            print(f"  ✗ Error contacting Spleeter service: {e}")
            raise

    def transcribe_lyrics(self, vocals_path):
        """
        Transcribe lyrics and timing using Whisper.
        Returns lyrics with word-level timestamps.
        """
        print("[Pre-Process Agent] Transcribing vocals with Whisper...")

        try:
            # Use base model for faster transcription
            model = whisper.load_model("base")
            result = model.transcribe(vocals_path, word_timestamps=True)

            lyrics_data = {
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language", "unknown"),
            }

            print(f"  ✓ Transcribed {len(lyrics_data['segments'])} segments")
            print(f"  ✓ Language: {lyrics_data['language']}")
            print(f"  ✓ Sample text: {lyrics_data['text'][:100]}...")
            return lyrics_data

        except Exception as e:
            print(f"  ✗ Whisper transcription failed: {e}")
            raise

    def process(self, song_path):
        """
        Main processing pipeline.
        """
        print("\n" + "=" * 60)
        print("STAGE 1: PRE-PROCESSING")
        print("=" * 60)

        vocals_path, instrumental_path = self.separate_audio(song_path)
        lyrics_data = self.transcribe_lyrics(vocals_path)

        return {
            "vocals_path": vocals_path,
            "instrumental_path": instrumental_path,
            "lyrics_data": lyrics_data,
        }


# =====================================================
# 2️⃣ LYRIC GENERATION AGENT
# =====================================================
class LyricGenerationAgent:
    """
    Lyric Generation Agent: Rewrites lyrics to match a theme using Google Gemini
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠ No Gemini API key found. Set GEMINI_API_KEY in your .env file.")

    def rewrite_lyrics(self, original_lyrics, theme):
        print("\n" + "=" * 60)
        print("STAGE 2: LYRIC GENERATION")
        print("=" * 60)
        print(f"[Lyric Gen Agent] Rewriting lyrics with theme: {theme}")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""
            Rewrite the following song lyrics to fit the theme: "{theme}"
            Maintain the rhythm, syllable count, rhyme scheme and flow.

            Original:
            {original_lyrics['text']}
            """

            response = model.generate_content(prompt)
            rewritten = response.text.strip() if response and hasattr(response, "text") else None

            if not rewritten:
                raise ValueError("Empty response from Gemini")

            print(f"  ✓ New lyrics generated.")
            return {"original": original_lyrics, "rewritten": rewritten, "theme": theme}

        except Exception as e:
            print(f"  ✗ Error during lyric generation: {e}")
            # Fallback to original lyrics
            return {"original": original_lyrics, "rewritten": original_lyrics['text'], "theme": theme}

    def process(self, lyrics_data, theme):
        result = self.rewrite_lyrics(lyrics_data, theme)
        return result


# =====================================================
# 3️⃣ VOICE SYNTHESIS AGENT (ElevenLabs Placeholder)
# =====================================================

class VoiceSynthAgent:
    """
    A placeholder for a Voice Synthesis Agent (e.g., ElevenLabs).
    It generates a dummy audio file or uses a test file for the pipeline.
    """

    def __init__(self, api_key=None):
        # This assumes an ELEVENLABS_API_KEY environment variable is set
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            print("⚠ No ELEVENLABS_API_KEY found. Voice synthesis will rely on local test file.")

    def process(self, lyrics_data, description=""):
        print("\n" + "=" * 60)
        print("STAGE 3: VOICE SYNTHESIS")
        print("=" * 60)

        # Get the rewritten lyrics
        lyrics = lyrics_data.get("rewritten", lyrics_data.get("original", {}).get("text", "Default test lyrics."))

        # Define output path
        local_voice_path = Path("output") / "generated_vocals.mp3"
        os.makedirs(local_voice_path.parent, exist_ok=True)

        # ✅ If the vocals already exist, assume they are correct and skip generation
        if os.path.exists(local_voice_path):
            print(f"  🎤 Using existing local vocal file: {local_voice_path}")
            return str(local_voice_path)

        # 🧠 Attempt generation using ElevenLabs
        if self.api_key:
            print("  🧠 Attempting to generate new AI vocals with ElevenLabs...")
            try:
                import requests
                # This is a highly simplified and possibly incorrect endpoint/payload
                # You should replace this with a proper ElevenLabs SDK call if using in production
                url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                voice_id = "EXAVITQu4vr4xnSDzIErd"  # Adam (Default)

                headers = {
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": lyrics,
                    "model_id": "eleven_multilingual_v2"
                }

                response = requests.post(url.format(voice_id=voice_id), json=payload, headers=headers)

                if response.status_code == 200:
                    with open(local_voice_path, "wb") as f:
                        f.write(response.content)
                    print(f"  ✓ New vocals saved to {local_voice_path}")
                    return str(local_voice_path)
                else:
                    print(f"  ❌ ElevenLabs failed ({response.status_code}): {response.text}")

            except Exception as e:
                print(f"  ✗ Error during voice synthesis: {e}")

        # ⚠️ Fallback: Create a dummy silent audio file
        print("  ⚠️ No API key or generation failed. Creating a 10-second silent audio placeholder.")
        try:
            # Create 10 seconds of silence (44.1kHz, stereo)
            silent_audio = AudioSegment.silent(duration=10000, frame_rate=44100)
            silent_audio.export(local_voice_path, format="mp3")
            print(f"  ✓ Dummy silent vocals saved to {local_voice_path}")
            return str(local_voice_path)
        except Exception as e:
            print(f"  ❌ Fallback failed: {e}")
            return None


# =====================================================
# 4️⃣ ALIGNER AGENT - SIMPLE DURATION MATCHING
# =====================================================

class AlignerAgent:
    def __init__(self):
        pass

    def _load_vocals(self, path):
        """Load vocals and ensure mono."""
        y, sr = librosa.load(path, sr=None, mono=True)
        duration = len(y) / sr
        print(f"✓ Loaded vocals: {path}")
        print(f"  - Duration: {duration:.2f} seconds")
        print(f"  - Sample rate: {sr} Hz")
        return y, sr

    def process(self, vocals_path, lyrics_data):
        print("\n" + "=" * 60)
        print("STAGE 4: ALIGNMENT (Simple Duration Matching)")
        print("=" * 60)

        try:
            # Load the new AI vocals
            y_vocals, sr_vocals = self._load_vocals(vocals_path)

            # Get the original song duration from timing data
            original_duration = 0
            if isinstance(lyrics_data, dict) and "segments" in lyrics_data:
                for seg in lyrics_data["segments"]:
                    seg_end = seg.get("end", 0)
                    if seg_end > original_duration:
                        original_duration = seg_end
                print(f"✓ Original song duration: {original_duration:.2f} seconds")
            else:
                # Fallback to the duration of the new vocals if timing data is missing
                original_duration = len(y_vocals) / sr_vocals
                print(f"⚠️ Could not determine original duration; using new vocals duration: {original_duration:.2f}s")

            current_duration = len(y_vocals) / sr_vocals
            target_samples = int(original_duration * sr_vocals)
            current_samples = len(y_vocals)

            print(f"✓ Current vocal samples: {current_samples} ({current_duration:.2f}s)")
            print(f"✓ Target samples needed: {target_samples} ({original_duration:.2f}s)")

            # Simple approach: repeat or trim to match length
            if current_samples < target_samples:
                # Need to extend - loop the vocals
                repeats_needed = int(np.ceil(target_samples / current_samples))
                print(f"  ⚙️  Looping vocals {repeats_needed} times to fill duration...")
                aligned_audio = np.tile(y_vocals, repeats_needed)[:target_samples]
            else:
                # Need to shorten - just trim
                print(f"  ⚙️  Trimming vocals to match duration...")
                aligned_audio = y_vocals[:target_samples]

            # Verify final duration
            final_duration = len(aligned_audio) / sr_vocals
            print(f"✓ Final duration: {final_duration:.2f} seconds")

            # Save aligned output (using librosa/soundfile)
            aligned_output_wav = Path("output") / "aligned_vocals.wav"
            sf.write(str(aligned_output_wav), aligned_audio, sr_vocals)
            print(f"✓ Aligned vocals saved: {aligned_output_wav}")

            return str(aligned_output_wav)

        except Exception as e:
            print(f"✗ Error in alignment stage: {e}")
            import traceback
            traceback.print_exc()
            print(f"⚠️ Falling back to original vocals path: {vocals_path}")
            return vocals_path


# =====================================================
# 5️⃣ MIXER AGENT - ENHANCED VERSION
# =====================================================

class MixerAgent:
    def __init__(self, vocal_boost_db=2, instrumental_reduce_db=-3):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.vocal_boost_db = vocal_boost_db
        self.instrumental_reduce_db = instrumental_reduce_db

    def process(self, vocals_path, instrumental_path, output_name="final_mix"):
        print("\n" + "=" * 60)
        print("STAGE 5: MIXING")
        print("=" * 60)

        try:
            # Load audio files
            print(f"  📂 Loading vocals from: {vocals_path}")
            # Ensure from_file is used for MP3/WAV versatility
            vocals = AudioSegment.from_file(vocals_path)

            print(f"  📂 Loading instrumental from: {instrumental_path}")
            instrumental = AudioSegment.from_file(instrumental_path)

            # Match sample rates and channels
            if vocals.frame_rate != instrumental.frame_rate:
                vocals = vocals.set_frame_rate(instrumental.frame_rate)
            if vocals.channels != instrumental.channels:
                if vocals.channels == 1:
                    vocals = vocals.set_channels(2)
                if instrumental.channels == 1:
                    instrumental = instrumental.set_channels(2)

            # Trim or pad to match lengths
            target_length = min(len(vocals), len(instrumental))
            vocals = vocals[:target_length]
            instrumental = instrumental[:target_length]
            print(f"  ✂️  Mixed duration: {target_length}ms")

            # Apply volume adjustments
            vocals = vocals + self.vocal_boost_db
            instrumental = instrumental + self.instrumental_reduce_db

            # Apply light compression to vocals for consistency
            vocals = compress_dynamic_range(vocals, threshold=-20.0, ratio=3.0, attack=5.0, release=50.0)

            # Mix the tracks
            mixed = instrumental.overlay(vocals, position=0)

            # Normalize the final mix
            mixed = normalize(mixed, headroom=0.1)

            # Export final mix
            wav_output_path = self.output_dir / f"{output_name}.wav"
            mixed.export(wav_output_path, format="wav", parameters=["-ar", "44100", "-ac", "2"])

            mp3_output_path = self.output_dir / f"{output_name}.mp3"
            mixed.export(mp3_output_path, format="mp3", bitrate="320k")

            print(f"  ✅ Final mix saved successfully to {mp3_output_path}")
            return str(mp3_output_path)

        except Exception as e:
            print(f"  ❌ Error during mixing: {e}")
            import traceback
            traceback.print_exc()
            return None


# =====================================================
# 6️⃣ SUNO SONG CREATION AGENT (For full song gen, not used in pipeline)
# =====================================================
class CreateSongAgent:
    """
    A class to interact with the Suno API, handling file uploads
    and requests to add vocals to an instrumental track.

    🔥 FIX IMPLEMENTED HERE for 502 error during upload.
    """

    def __init__(self, api_key=None, base_url="https://api.sunoapi.org"):
        self.api_key = api_key or os.environ.get("SUNO_API_KEY")
        self.base_url = base_url

        if not self.api_key:
            print("⚠ No SUNO API key found.")

    def _upload_local_file(self, local_file_path):
        """
        (Step 1) Uploads a local audio file using multipart/form-data.
        """
        if not self.api_key:
            print("❌ Cannot upload file: API key is missing.")
            return None

        if not os.path.exists(local_file_path):
            print(f"❌ File not found at path: {local_file_path}")
            return None

        # Use the primary URL, or the mirror suggested by the developer:
        # "https://api.kie.ai/api/file-stream-upload"
        upload_url = f"{self.base_url}/api/file-stream-upload"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            # DO NOT set Content-Type; 'requests' handles multipart boundary
        }

        try:
            with open(local_file_path, 'rb') as f:
                # The field name MUST be 'file' as per the developer
                files = {'file': (os.path.basename(local_file_path), f)}

                print(f"Uploading {local_file_path} to {upload_url}...")
                # Add a timeout to catch network-related 502s
                response = requests.post(upload_url, headers=headers, files=files, timeout=120)

                # Explicitly handle 502 as per developer notes
                if response.status_code == 502:
                    print("❌ Received 502 Bad Gateway. Check file size (<100MB) or use the mirror endpoint.")
                    return None

                response.raise_for_status()  # Check for 4xx/5xx errors

                response_data = response.json()

                if response_data.get("success") and "data" in response_data and "downloadUrl" in response_data["data"]:
                    download_url = response_data["data"]["downloadUrl"]
                    print(f"✅ File uploaded successfully. URL: {download_url}")
                    return download_url
                else:
                    print(f"❌ File upload failed. API response: {response_data}")
                    return None

        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP error during upload: {http_err}. Content: {response.content}")
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Network error during upload: {req_err}")
        except Exception as e:
            print(f"❌ Unexpected error during file upload: {e}")

        return None

    def send_request(self, song_description, local_file_path):
        """
        (Step 2) Sends a request to add vocals using the uploaded instrumental file.
        """
        # --- STEP 1: UPLOAD THE FILE ---
        instrumental_url = self._upload_local_file(local_file_path)

        if not instrumental_url:
            print("❌ Halting request: File upload failed.")
            return None

        # --- STEP 2: SEND THE 'ADD VOCALS' REQUEST ---
        print(f"Sending 'add-vocals' request for {instrumental_url}...")

        url = f"{self.base_url}/api/v1/generate/add-vocals"

        payload = {
            "prompt": song_description,
            "title": "AI Remix",
            "negativeTags": "Heavy Metal, Aggressive Vocals",
            "style": "Pop",
            "vocalGender": "m",
            "uploadUrl": instrumental_url,
            # Other parameters omitted for brevity, adjust as needed
            "model": "V4_5PLUS"
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            print("✅ 'Add-vocals' request successful!")
            return response.json()

        except requests.exceptions.RequestException as req_err:
            print(f"❌ Error on 'add-vocals' request: {req_err}")
            return None


# =====================================================
# MAIN PIPELINE
# =====================================================
class SongPipeline:
    def __init__(self, gemini_api_key=None):

        # Load keys from environment, but only for demonstration
        gemini_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")

        self.preprocess_agent = PreProcessAgent()
        self.lyric_gen_agent = LyricGenerationAgent(api_key=gemini_key)
        # Note: VoiceSynthAgent needs ELEVENLABS_API_KEY from environment
        self.voice_synth_agent = VoiceSynthAgent(api_key=elevenlabs_key)
        self.aligner_agent = AlignerAgent()
        self.mixer_agent = MixerAgent()

    def run(self, song_path, theme, artist_name="Unknown Artist"):
        print("\n" + "=" * 60)
        print("AI SONG PIPELINE STARTED")
        print("=" * 60)

        # 1. Pre-process (Separate Vocals/Instrumental, Transcribe Lyrics)
        preprocess = self.preprocess_agent.process(song_path)
        lyrics_data = preprocess["lyrics_data"]
        instrumental_path = preprocess["instrumental_path"]

        # 2. Lyric Generation (Rewrite lyrics with Gemini)
        rewritten_lyrics = self.lyric_gen_agent.process(lyrics_data, theme)

        # 3. Voice Synthesis (Generate new vocals - uses ElevenLabs/Placeholder)
        synth_vocals_path = self.voice_synth_agent.process(rewritten_lyrics, description="")

        if not synth_vocals_path:
            print("❌ Pipeline failed: Voice synthesis did not produce a valid file.")
            return None

        # 4. Alignment (Match new vocals duration to original track duration)
        # We pass the full lyrics_data for the original song's timing (end time)
        aligned_vocals_path = self.aligner_agent.process(synth_vocals_path, lyrics_data)

        if not aligned_vocals_path:
            print("❌ Pipeline failed: Alignment stage failed.")
            return None

        # 5. Mixing (Combine aligned new vocals with the original instrumental)
        final_mix_path = self.mixer_agent.process(
            aligned_vocals_path,
            instrumental_path,
            f"{Path(song_path).stem}_remix"
        )

        print("\n✓ PIPELINE COMPLETE.")
        return final_mix_path


# =====================================================
# ENTRY POINT
# =====================================================
def main():
    parser = argparse.ArgumentParser(description="AI Song Pipeline")
    parser.add_argument("--song", required=True, help="Path to the original song (e.g., my_song.mp3)")
    parser.add_argument("--theme", required=True, help="New theme for the lyrics (e.g., 'Life on Mars')")
    parser.add_argument("--artist", default="Unknown Artist", help="Original artist name")
    args = parser.parse_args()

    # NOTE: You must have a running Spleeter service for PreProcessAgent to work!
    pipeline = SongPipeline()
    output = pipeline.run(args.song, args.theme, args.artist)

    if output:
        print(f"\n✅ Final output saved to: {output}")
    else:
        print("\n❌ Pipeline execution failed at a critical stage.")


if __name__ == "__main__":
    # Example usage (you would run this from your terminal):
    # python your_script_name.py --song /path/to/your/song.mp3 --theme "The Joy of Coding"
    # Ensure you have .env file with GEMINI_API_KEY, ELEVENLABS_API_KEY, and a running Spleeter service.
    # For testing the CreateSongAgent (Suno) function:
    # suno_agent = CreateSongAgent()
    # suno_agent.send_request("A high-energy 80s rock anthem about space travel", "./path/to/my/instrumental.mp3")

    # sys.exit(main()) # Uncomment to run the full pipeline
    print("\nScript loaded. Run with: python your_script.py --song <path> --theme <theme>")