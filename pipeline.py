#!/usr/bin/env python3
"""
AI Song Pipeline - Transforms songs with AI-generated lyrics
"""

import argparse
import os
import sys
import requests
import base64  # NEW: For Base64 file upload
import json
from pathlib import Path
from dotenv import load_dotenv
import whisper
import time

# Load environment variables
load_dotenv()


# =====================================================
# 1️⃣ PRE-PROCESS AGENT (FIXED: Added robust Spleeter error handling)
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

        retries = 3
        delay = 5

        for attempt in range(retries):
            try:
                with open(song_path, "rb") as f:
                    files = {"file": (Path(song_path).name, f, "audio/mpeg")}

                    print(f"  ⚙ Attempting Spleeter split (Attempt {attempt + 1}/{retries})...")
                    response = requests.post(self.spleeter_service_url, files=files, timeout=600)  # Added timeout

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

            except requests.exceptions.RequestException as e:
                # Catch network errors (like ConnectionResetError 10054)
                print(f"  ✗ Network error contacting Spleeter (Attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    print(f"  Waiting {delay}s before retry...")
                    time.sleep(delay)
                    continue
                else:
                    raise  # Re-raise the exception after all retries fail
            except Exception as e:
                # Catch Spleeter service errors (like 500)
                print(f"  ✗ Error contacting Spleeter service: {e}")
                raise

    def transcribe_lyrics(self, vocals_path):
        """
        Transcribe lyrics and timing using Whisper.
        Returns lyrics with word-level timestamps.
        """
        print("[Pre-Process Agent] Transcribing vocals with Whisper...")

        try:
            model = whisper.load_model("base")
            result = model.transcribe(vocals_path, word_timestamps=True)

            lyrics_data = {
                "text": result["text"].strip(),  # Strip whitespace from text
                "segments": result.get("segments", []),
                "language": result.get("language", "unknown"),
            }

            # Check if transcription failed to extract meaningful text
            is_empty = not lyrics_data['text'] or lyrics_data['text'].startswith("...") or lyrics_data['text'] == " "

            print(f"  ✓ Transcribed {len(lyrics_data['segments'])} segments")
            print(f"  ✓ Language: {lyrics_data['language']}")
            print(f"  ✓ Sample text: {lyrics_data['text'][:100]}...")
            return lyrics_data

        except Exception as e:
            print(f"  ✗ Whisper transcription failed: {e}")
            # Return empty data structure so the pipeline can proceed
            return {"text": "", "segments": [], "language": "en"}

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
# 2️⃣ LYRIC GENERATION AGENT (FIXED: Added logic for empty/instrumental tracks)
# =====================================================
class LyricGenerationAgent:
    """
    Lyric Generation Agent: Rewrites lyrics to match a theme using Google Gemini
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠ No Gemini API key found. Set GEMINI_API_KEY in your .env file.")

        # Initialize Gemini once
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            print("  ✓ Gemini model initialized (gemini-2.5-flash).")
        except Exception as e:
            self.model = None
            print(f"  ✗ Gemini initialization failed: {e}")

    def _call_gemini(self, prompt):
        """Helper for calling Gemini."""
        if not self.model:
            raise Exception("Gemini model not available.")

        response = self.model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, "text") else None

    def rewrite_lyrics(self, original_text, theme):
        """Rewrites existing lyrics."""
        prompt = f"""
        Rewrite the following song lyrics to fit the theme: "{theme}"
        Maintain the rhythm, syllable count, rhyme scheme and flow.

        Original Lyrics:
        {original_text}
        """
        return self._call_gemini(prompt)

    def generate_new_lyrics(self, theme, artist="Unknown Artist"):
        """Generates new lyrics from scratch."""
        prompt = f"""
        Write new song lyrics (Verse, Chorus, Verse, Chorus) about the theme of "{theme}".
        The style should be a tribute to the artist {artist}, if possible.
        The lyrics should be clean and fit a standard popular song structure.
        """
        return self._call_gemini(prompt)

    def process(self, lyrics_data, theme, artist_name="Unknown Artist"):
        print("\n" + "=" * 60)
        print("STAGE 2: LYRIC GENERATION")
        print("=" * 60)

        original_text = lyrics_data.get("text", "").strip()
        rewritten = ""

        # Determine if we should rewrite or generate new
        if not original_text or len(original_text) < 5:
            print(f"[Lyric Gen Agent] Original lyrics are empty/minimal. Generating new lyrics for theme: {theme}")

            try:
                rewritten = self.generate_new_lyrics(theme, artist_name)
                print("  ✓ New lyrics generated.")
            except Exception as e:
                print(f"  ✗ Error during new lyric generation: {e}")

        else:
            print(f"[Lyric Gen Agent] Rewriting lyrics with theme: {theme}")

            try:
                rewritten = self.rewrite_lyrics(original_text, theme)
                print("  ✓ Rewritten lyrics generated.")
            except Exception as e:
                print(f"  ✗ Error during lyric rewrite: {e}")

        if not rewritten or len(rewritten) < 5:
            print("❌ Halting pipeline: Lyrics are empty after generation.")
            # Critical error: stop the pipeline by raising an exception
            raise Exception("Rewritten lyrics (Suno prompt) are empty after generation.")

        print(f"  ✓ Sample: {rewritten[:100].replace('\n', ' ')}...")

        return {"original": lyrics_data, "rewritten": rewritten, "theme": theme}


# =====================================================
# ⭐️ NEW VOICE AGENT: SUNO (FIXED: Uses File Stream Upload with correct URL)
# =====================================================
class CreateSongAgent:
    """
    A class to interact with the Suno API, handling file uploads
    and requests to add vocals to an instrumental track.
    """

    def __init__(self, api_key=None, base_url="https://api.sunoapi.org"):
        self.api_key = api_key or os.environ.get("SUNO_API_KEY")
        # Use the base URL for the 'add-vocals' request (which may or may not be correct)
        self.base_url = base_url

        if not self.api_key:
            print("⚠ No SUNO API key found. Set SUNO_API_KEY in your .env file.")

    def _upload_local_file(self, local_file_path):
        """
        (Step 1) Uploads a local audio file using the File Stream Upload method.
        This uses the URL confirmed in the documentation snippet 1.2.
        """
        if not self.api_key:
            print("❌ Cannot upload file: API key is missing.")
            return None

        if not os.path.exists(local_file_path):
            print(f"❌ File not found at path: {local_file_path}")
            return None

        # --- CORRECT URL FROM DOCUMENTATION SNIPPET ---
        upload_url = "https://sunoapiorg.redpandaai.co/api/file-stream-upload"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        retries = 3
        delay = 5

        for attempt in range(retries):
            try:
                # We open the file in binary-read mode ('rb')
                with open(local_file_path, 'rb') as f:
                    # 'files' is the correct way to send multipart/form-data
                    files = {
                        'file': (os.path.basename(local_file_path), f),
                        # Required form data parameters based on the cURL example:
                        'uploadPath': ('images/user-uploads'),
                        'fileName': (os.path.basename(local_file_path))
                    }

                    print(f"Uploading {local_file_path} to {upload_url} (Attempt {attempt + 1}/{retries})...")
                    # Do NOT include Content-Type header when using 'files' parameter, requests handles it.
                    response = requests.post(upload_url, headers=headers, files=files)

                    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

                    response_data = response.json()

                    # Check for success based on the documented response structure
                    if response_data.get("success") is True and "downloadUrl" in response_data.get("data", {}):
                        download_url = response_data["data"]["downloadUrl"]
                        print(f"✅ File uploaded successfully. URL received: {download_url[:50]}...")
                        return download_url
                    else:
                        print(f"❌ File upload failed (API logic error). API response: {response_data}")
                        return None  # Don't retry on logic error

            except requests.exceptions.HTTPError as http_err:
                print(f"❌ HTTP error occurred during upload: {http_err}")
                if attempt < retries - 1:
                    print(f"Server error. Waiting {delay}s to retry...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Upload failed after {retries} attempts. Response: {response.content.decode()}")

            except requests.exceptions.RequestException as req_err:
                print(f"❌ A network error occurred during upload: {req_err}")
                if attempt < retries - 1:
                    print(f"Waiting {delay}s to retry...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Network failure after {retries} attempts.")
            except Exception as e:
                print(f"❌ An unexpected error occurred during file upload: {e}")
                return None

        return None  # Should not be reached if exceptions are raised correctly

    def send_request(self, song_description, local_file_path, callback_url=None):
        """
        (Step 2) Sends a request to add vocals using the uploaded file's URL.
        """
        # --- FIX 1: Use the corrected stream upload method ---
        instrumental_url = self._upload_local_file(local_file_path)

        if not instrumental_url:
            print("❌ Halting request: File upload failed.")
            return None

        print(f"Sending 'add-vocals' request...")
        # Endpoint remains the original base_url for the main API call
        url = f"{self.base_url}/api/v1/generate/add-vocals"

        # ... (payload and headers remain the same for the add-vocals call) ...

        payload = {
            "prompt": song_description,
            "title": "AI Generated Song",
            "negativeTags": "acoustic, spoken word",
            "style": "Pop",
            "vocalGender": "m",
            "styleWeight": 0.61,
            "weirdnessConstraint": 0.72,
            "audioWeight": 0.65,
            "uploadUrl": instrumental_url,
            "model": "V4_5PLUS"
        }

        if callback_url:
            payload["callBackUrl"] = callback_url

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            response_json = response.json()

            if response_json.get('code') == 200 and 'taskId' in response_json.get("data", {}):
                print(f"✅ 'Add-vocals' task started. Task ID: {response_json['data']['taskId']}")
                return response_json
            else:
                print(f"❌ 'Add-vocals' API failed: {response_json.get('msg', 'Unknown API error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error occurred on 'add-vocals': {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
        return None


# =====================================================
# MAIN PIPELINE
# =====================================================
class SongPipeline:
    def __init__(self, gemini_api_key=None):
        print("Initializing AI Song Pipeline...")
        self.preprocess_agent = PreProcessAgent()
        # Pass the artist_name when creating the lyric agent
        self.lyric_gen_agent = LyricGenerationAgent(api_key=gemini_api_key)

        self.suno_agent = CreateSongAgent()
        print("Pipeline initialized.")

    def run(self, song_path, theme, artist_name="Unknown Artist"):
        print("\n" + "=" * 60)
        print("AI SONG PIPELINE (SUNO WORKFLOW) STARTED")
        print("=" * 60)

        # --- STAGE 1: PRE-PROCESSING ---
        try:
            preprocess = self.preprocess_agent.process(song_path)
            instrumental_path = preprocess["instrumental_path"]
            lyrics_data = preprocess["lyrics_data"]
        except Exception as e:
            print(f"❌ Pipeline failed during Pre-Processing: {e}")
            return None

        # --- STAGE 2: LYRIC GENERATION ---
        # Pass artist_name to the process method for better new lyric generation
        try:
            rewritten_data = self.lyric_gen_agent.process(lyrics_data, theme, artist_name)
            suno_prompt = rewritten_data["rewritten"]
        except Exception as e:
            print(f"❌ Pipeline failed during Lyric Generation: {e}")
            return None

        # --- STAGE 3: SUNO SONG CREATION ---
        print("\n" + "=" * 60)
        print("STAGE 3: CREATING SONG WITH SUNO")
        print("=" * 60)

        final_song_data = self.suno_agent.send_request(
            song_description=suno_prompt,
            local_file_path=instrumental_path
        )

        print("\n✓ PIPELINE COMPLETE.")
        return final_song_data


# =====================================================
# ENTRY POINT
# =====================================================
def main():
    parser = argparse.ArgumentParser(description="AI Song Pipeline")
    parser.add_argument("--song", required=True, help="Path to the input song file (e.g., my_song.mp3)")
    parser.add_argument("--theme", required=True, help="The theme to rewrite the lyrics (e.g., 'a rainy day')")
    parser.add_argument("--artist", default="Unknown Artist", help="Name of the original artist (for style reference)")
    args = parser.parse_args()

    # Pass the API key from environment to the pipeline, which distributes it
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    pipeline = SongPipeline(gemini_api_key=gemini_api_key)
    print(f"Starting pipeline for song: '{args.song}' with theme: '{args.theme}'")
    output = pipeline.run(args.song, args.theme, args.artist)

    # Display the final output for the user
    output_display = json.dumps(output, indent=2) if output else "None"
    print(f"\nFinal Suno Response (contains task ID): {output_display}")


if __name__ == "__main__":
    sys.exit(main())