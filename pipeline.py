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

            print(f"  ✓ New lyrics generated.{rewritten}")
            return {"original": original_lyrics, "rewritten": rewritten, "theme": theme}

        except Exception as e:
            print(f"  ✗ Error during lyric generation: {e}")
            return {"original": original_lyrics, "rewritten": original_lyrics['text'], "theme": theme}

    def process(self, lyrics_data, theme):
        return self.rewrite_lyrics(lyrics_data, theme)


# =====================================================
# 3️⃣ VOICE SYNTHESIS AGENT
# =====================================================
import os
from pathlib import Path
# import requests

# url = "https://api.sunoapi.org/api/v1/generate/add-vocals"

# payload = {
#     "prompt": "A calm and relaxing piano track with soothing vocals",
#     "title": "Relaxing Piano with Vocals",
#     "negativeTags": "Heavy Metal, Aggressive Vocals",
#     "style": "Jazz",
#     "vocalGender": "m",
#     "styleWeight": 0.61,
#     "weirdnessConstraint": 0.72,
#     "audioWeight": 0.65,
#     "uploadUrl": "https://example.com/instrumental.mp3",
#     "callBackUrl": "https://api.example.com/callback",
#     "model": "V4_5PLUS"
# }
# headers = {
#     "Authorization": "Bearer <token>",
#     "Content-Type": "application/json"
# }

# response = requests.post(url, json=payload, headers=headers)

# print(response.json())

class MusicGen:
    """
    Music gen using suno ai
    """

    def __init__(self, api_key=None, suno_api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.suno_api_key = suno_api_key or os.environ.get("SUNO_API_KEY")
        if not self.suno_api_key:
            print("No suno API Key found")
        if not self.api_key:
            print("⚠ No Gemini API key found. Set GEMINI_API_KEY in your .env file.")

    def create_song_details(self, lyrics, songName, artistName):
        print("\n" + "=" * 60)
        print("STAGE X: MUSIC GENERATION")
        print("=" * 60)
        print(f"[MUSIC GEN AGENT] Generating description for '{songName}' by {artistName}...")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""
    You are a world-class music producer, sound designer, and creative director with a deep understanding of tone, mood, and style.

    Given the **artist name** and **song title**, generate a **cinematic and emotionally detailed description** of the track’s sound — without naming the artist or song directly.  
    The goal is to brief an AI music system that will recreate and remix the track with new lyrics.

    Your output must be vivid and technically descriptive, as if explaining the song to a producer who will rebuild it from scratch.

    ---

    ### TASKS

    1. **Describe the sound and feeling**
    - Explain the **musical atmosphere** (tempo, rhythm, instrumentation, production style)
    - Capture the **emotional tone** and **vocal style** (delivery, expression, energy)
    - Provide **cultural or temporal context** (era, influences, location)
    - Summarize the **story or message** the music conveys

    2. **Generate metadata**
    - "title": A suitable remix title inspired by the original song
    - "style": The musical style or genre (e.g., "Jazz", "Hip-Hop", "R&B", "Pop", "Electronic")
    - "negativeTags": Musical directions or styles to AVOID (e.g., "Heavy Metal, Rock, Country")
    - "vocalGender":  
        - "m" for male voice  
        - "f" for female voice  
        Infer this naturally from the artist’s name or typical vocal range if known.

    3. **Append new lyrics**
    After the song description, include:
    “Now perform the remix with these new lyrics, keeping the same emotional and sonic energy:”  
    Then insert the lyrics below exactly as provided.

    ---

    ### INPUT
    Artist: {artistName}  
    Song: {songName}  
    Lyrics: {lyrics}

    ---

    ### OUTPUT FORMAT
    Return your final result strictly as valid **JSON**, using this structure:

    {{
    "description": "<a vivid paragraph describing the song’s sound, tone, and mood>",
    "title": "<a fitting remix title>",
    "negativeTags": "<comma-separated list of unwanted genres or traits>",
    "style": "<musical style or genre>",
    "vocalGender": "<m or f>"
    }}
    """

            # Generate response
            response = model.generate_content(prompt)
            raw_output = response.text.strip() if response and hasattr(response, "text") else None

            if not raw_output:
                raise ValueError("Empty response from Gemini")

            import json
            try:
                description_data = json.loads(raw_output)
            except json.JSONDecodeError:
                print("  ⚠️ Model returned non-JSON output. Using raw text instead.")
                description_data = {"description": raw_output}

            # Debug print
            print(f"  ✓ New description generated:\n{description_data.get('description', raw_output)}\n")

            # Build structured output (with fallbacks)
            return {
                "description": description_data.get("description", raw_output),
                "title": description_data.get("title", f"{songName} (Remix)"),
                "negativeTags": description_data.get("negativeTags", "Heavy Metal, Rock, Country"),
                "style": description_data.get("style", "Contemporary Soul"),
                "vocalGender": description_data.get("vocalGender", "m"),
                "artist": artistName,
                "song name": songName
            }

        except Exception as e:
            print(f"  ✗ Error during description generation: {e}")

            # Default fallback output if generation or parsing fails
            default_description = (
                f"An emotionally rich, rhythm-driven track blending soulful melodies with modern production. "
                f"It carries an introspective yet powerful energy — balancing vulnerability and ambition. "
                f"The vocals are expressive and dynamic, layered over atmospheric synths and punchy percussion, "
                f"capturing the sound of an artist striving for meaning, growth, and connection through music.\n\n"
                f"Now perform the remix with these new lyrics, keeping the same emotional and sonic energy:\n{lyrics}"
            )

            return {
                "description": default_description,
                "title": f"{songName} (Remix)",
                "negativeTags": "Heavy Metal, Rock, Country",
                "style": "Contemporary Soul",
                "vocalGender": "m",
                "artist": artistName,
                "song name": songName
            }
    # def song_creation(lyrics, songName, artistName, instruMental):




class VoiceSynthAgent:
    """
    Voice Synthesis Agent:
    - Uses Gemini to analyze artist's voice style.
    - Selects a matching ElevenLabs voice.
    - Synthesizes vocals using rewritten lyrics.
    """

    def __init__(self, gemini_api_key=None, elevenlabs_api_key=None):
        import google.generativeai as genai
        from elevenlabs.client import ElevenLabs  # ✅ correct import

        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")

        # Initialize Gemini (optional)
        self.gemini_model = None
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                print("  ✓ Gemini initialized for voice analysis.")
            except Exception as e:
                print(f"  ✗ Gemini initialization failed: {e}")

        # Initialize ElevenLabs
        self.eleven_client = None
        try:
            self.eleven_client = ElevenLabs(api_key=self.elevenlabs_api_key)
            print("  ✓ ElevenLabs initialized for TTS.")
        except Exception as e:
            print(f"  ✗ ElevenLabs init error: {e}")

    # =============================================================
    # VOICE SELECTION STAGE
    # =============================================================

    def analyze_voice(self, artist_name: str) -> str:
        """
        Use Gemini to describe artist's voice (tone, timbre, range).
        """
        if not self.gemini_model:
            return f"A voice similar to {artist_name}"

        prompt = f"Describe {artist_name}'s vocal tone, timbre, and range in detail."
        try:
            resp = self.gemini_model.generate_content(prompt)
            return resp.text.strip()
        except Exception:
            return f"A voice similar to {artist_name}"

    def pick_best_voice(self, voice_description: str) -> str:
        """
        Use Gemini to select the most fitting ElevenLabs voice.
        """
        if not self.gemini_model or not self.eleven_client:
            return "pNInz6obpgDQGcFmaJgB"  # Default Adam

        try:
            voices = self.eleven_client.voices.get_all().voices
            voice_list = "\n".join(
                [f"- {v.name}: {getattr(v, 'description', 'No description')}" for v in voices]
            )

            prompt = f"""
            Based on this voice description:
            {voice_description}

            Choose the best matching ElevenLabs voice from:
            {voice_list}

            Return only the voice name.
            """

            resp = self.gemini_model.generate_content(prompt)
            match_name = resp.text.strip().lower()

            for v in voices:
                if v.name.lower() == match_name:
                    print(f"  ✓ Voice selected: {v.name}")
                    return v.voice_id

            print("  ⚠ No exact match found, using default voice.")
            return "pNInz6obpgDQGcFmaJgB"

        except Exception as e:
            print(f"  ✗ Voice match error: {e}")
            return "pNInz6obpgDQGcFmaJgB"

    # =============================================================
    # SYNTHESIS STAGE
    # =============================================================

    def synthesize_voice(self, lyrics: str, artist_name: str = None) -> str | None:
        """
        Generate vocals from lyrics using the best ElevenLabs voice.
        """
        print("\n" + "=" * 60)
        print("VOICE SYNTHESIS")
        print("=" * 60)

        if not self.eleven_client:
            print("  ✗ ElevenLabs client not initialized — cannot synthesize voice.")
            return None

        # Analyze & pick voice
        if artist_name:
            description = self.analyze_voice(artist_name)
            voice_id = self.pick_best_voice(description)
        else:
            voice_id = "pNInz6obpgDQGcFmaJgB"  # Default
            print("  ⚙ Using default ElevenLabs voice.")

        # Generate audio
        print(f"  🎤 Generating vocals using voice ID: {voice_id}")

        try:
            audio_generator = self.eleven_client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=lyrics,
                output_format="mp3_44100_128"
            )

            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "generated_vocals.mp3"

            audio_bytes = b"".join(audio_generator)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            print(f"  ✓ Vocals successfully saved to {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"  ✗ Voice synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    # =============================================================
    # PIPELINE INTERFACE
    # =============================================================

    def process(self, lyrics_data: dict, artist_name: str = None):
        """
        Pipeline entrypoint — expects `lyrics_data` from previous stage.
        """
        lyrics = (
            lyrics_data.get("rewritten")
            if isinstance(lyrics_data, dict)
            else str(lyrics_data)
        )

        return self.synthesize_voice(lyrics, artist_name or "Unknown Artist")

# =====================================================
# 4️⃣ ALIGNER AGENT
# =====================================================


class AlignerAgent:
    def process(self, vocals_path, timing_data_path):
        print("\n" + "=" * 60)
        print("STAGE 4: ALIGNMENT (Vocals → Timing Map)")
        print("=" * 60)

        try:
            # -------------------------------------------------------
            # 4.1 LOAD TIMING MAP
            # -------------------------------------------------------
            if not os.path.exists(timing_data_path):
                raise FileNotFoundError(f"Missing timing data: {timing_data_path}")

            with open(timing_data_path, "r") as f:
                timing_data = json.load(f)

            print(f"✓ Timing map loaded: {timing_data_path}")

            # -------------------------------------------------------
            # 4.2 LOAD AI VOCALS AND ALIGN USING DTW
            # -------------------------------------------------------
            y_vocals, sr_vocals = librosa.load(vocals_path, sr=None)
            print(f"✓ Loaded vocals: {vocals_path} ({len(y_vocals)} samples, {sr_vocals} Hz)")

            # Extract the target rhythm reference (e.g., beat times)
            ref_timing = np.array(timing_data.get("beat_times", []))
            if len(ref_timing) == 0:
                raise ValueError("No 'beat_times' key found in timing data.")

            # Extract onset envelope from AI vocals
            onset_env = librosa.onset.onset_strength(y=y_vocals, sr=sr_vocals)
            tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr_vocals)
            vocal_times = librosa.frames_to_time(beat_frames, sr=sr_vocals)

            # Use DTW to match AI vocal beats to reference timing
            distance, path = fastdtw(vocal_times, ref_timing, dist=euclidean)
            print(f"✓ DTW alignment completed (distance={distance:.2f})")

            # Stretch AI vocals to fit target rhythm
            stretch_ratio = len(ref_timing) / len(vocal_times)
            aligned_audio = librosa.effects.time_stretch(y_vocals, rate=stretch_ratio)

            aligned_output = "data/output/aligned_vocals.wav"
            os.makedirs(os.path.dirname(aligned_output), exist_ok=True)
            sf.write(aligned_output, aligned_audio, sr_vocals)
            print(f"✓ Aligned vocals saved: {aligned_output}")

            # -------------------------------------------------------
            # 4.3 VISUAL SYNC TEST
            # -------------------------------------------------------
            plt.figure(figsize=(10, 4))
            librosa.display.waveshow(aligned_audio, sr=sr_vocals, alpha=0.6)
            plt.title("Aligned Vocals Waveform")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.show()

            # -------------------------------------------------------
            # 4.4 FINAL ADJUSTMENT (OPTIONAL)
            # -------------------------------------------------------
            final_output = "data/output/final_vocals.wav"
            aligned_segment = AudioSegment.from_wav(aligned_output)

            # Optionally stretch or adjust pitch slightly
            final_segment = aligned_segment  # placeholder for extra tuning
            final_segment.export(final_output, format="wav")
            print(f"✓ Final vocals saved: {final_output}")

            # -------------------------------------------------------
            # ✅ RETURN OUTPUT
            # -------------------------------------------------------
            return final_output

        except Exception as e:
            print(f"✗ Error in alignment stage: {e}")
            return vocals_path


# =====================================================
# 5️⃣ MIXER AGENT
# =====================================================
class MixerAgent:
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def process(self, vocals_path, instrumental_path, output_name="final_mix"):
        print("\n" + "=" * 60)
        print("STAGE 5: MIXING")
        print("=" * 60)

        from pydub import AudioSegment

        vocals = AudioSegment.from_file(vocals_path)
        instrumental = AudioSegment.from_file(instrumental_path)

        if len(vocals) > len(instrumental):
            vocals = vocals[:len(instrumental)]
        else:
            instrumental = instrumental[:len(vocals)]

        mixed = instrumental.overlay(vocals)
        output_path = self.output_dir / f"{output_name}.wav"
        mixed.export(output_path, format="wav")
        print(f"  ✓ Final mix saved to: {output_path}")
        return str(output_path)


import os
import requests


class CreateSongAgent:
    """
    A class to interact with the Suno API, handling file uploads
    and requests to add vocals to an instrumental track.
    """

    def __init__(self, api_key=None, base_url="https://api.sunoapi.org"):
        """
        Initializes the agent.

        Args:
            api_key (str, optional): The Suno API key. If None, it will
                                     try to read from the SUNO_API_KEY
                                     environment variable.
            base_url (str, optional): The base URL for the Suno API.
        """
        self.api_key = api_key or os.environ.get("SUNO_API_KEY")
        self.base_url = base_url

        if not self.api_key:
            print("⚠ No SUNO API key found. Set SUNO_API_KEY in your .env file.")
            # Depending on your design, you might want to raise an error
            # raise ValueError("SUNO_API_KEY not found.")

    def _upload_local_file(self, local_file_path):
        """
        (Step 1) Uploads a local audio file to the API's file stream endpoint.

        This is a private helper method.

        Args:
            local_file_path (str): The path to the local .mp3 or .wav file.

        Returns:
            str: A public URL for the uploaded file, or None if it failed.
        """
        if not self.api_key:
            print("❌ Cannot upload file: API key is missing.")
            return None

        # Check if the file exists before trying to upload
        if not os.path.exists(local_file_path):
            print(f"❌ File not found at path: {local_file_path}")
            return None

        # This is the special endpoint for direct file uploads
        upload_url = f"{self.base_url}/api/file-stream-upload"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            # For multipart/form-data, 'requests' library sets the
            # 'Content-Type' header automatically when using the 'files' param.
        }

        try:
            # We open the file in binary-read mode ('rb')
            with open(local_file_path, 'rb') as f:
                # The 'files' parameter tells 'requests' to send a multipart/form-data
                # request. The API documentation suggests the field name is 'file'.
                files = {
                    'file': (os.path.basename(local_file_path), f)
                }

                print(f"Uploading {local_file_path} to {upload_url}...")
                response = requests.post(upload_url, headers=headers, files=files)

                # This will raise an error if the HTTP response is 4xx or 5xx
                response.raise_for_status()

                response_data = response.json()

                # We check the response structure based on the documentation
                # for a successful upload.
                if response_data.get("success") and "data" in response_data and "downloadUrl" in response_data["data"]:
                    download_url = response_data["data"]["downloadUrl"]
                    print(f"✅ File uploaded successfully. URL: {download_url}")
                    return download_url
                else:
                    print(f"❌ File upload failed. API response: {response_data}")
                    return None

        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP error occurred during upload: {http_err}")
            print(f"Response content: {response.content}")
        except requests.exceptions.RequestException as req_err:
            print(f"❌ A network error occurred during upload: {req_err}")
        except Exception as e:
            print(f"❌ An unexpected error occurred during file upload: {e}")

        return None

    def send_request(self, song_description, local_file_path):
        """
        (Step 2) Sends a request to add vocals using the uploaded local file.

        This is the main public method to call.

        Args:
            song_description (str): A description of the song/vocals to generate.
            local_file_path (str): The *local file path* to the instrumental MP3.

        Returns:
            dict: The JSON response from the API, or None if it failed.
        """

        # --- STEP 1: UPLOAD THE FILE ---
        # Call our helper method to get the public URL
        instrumental_url = self._upload_local_file(local_file_path)

        # If the upload failed, stop here.
        if not instrumental_url:
            print("❌ Halting request: File upload failed.")
            return None

        # --- STEP 2: SEND THE 'ADD VOCALS' REQUEST ---
        print(f"Sending 'add-vocals' request for {instrumental_url}...")

        url = f"{self.base_url}/api/v1/generate/add-vocals"

        # This is the payload for the 'add-vocals' endpoint
        payload = {
            "prompt": song_description,
            "title": "Relaxing Piano with Vocals",
            "negativeTags": "Heavy Metal, Aggressive Vocals",
            "style": "Jazz",
            "vocalGender": "m",
            "styleWeight": 0.61,
            "weirdnessConstraint": 0.72,
            "audioWeight": 0.65,
            "uploadUrl": instrumental_url,  # <-- We use the URL from Step 1!
            "callBackUrl": "https://api.example.com/callback",
            "model": "V4_5PLUS"
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            # Make the final POST request with the JSON payload
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

            print("✅ 'Add-vocals' request successful!")
            response_json = response.json()
            print("Response JSON:", response_json)
            return response_json

        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP error occurred on 'add-vocals': {http_err}")
            print(f"Response content: {response.content}")
        except requests.exceptions.RequestException as req_err:
            print(f"❌ A network error occurred on 'add-vocals': {req_err}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

        return None


# --- Example Usage ---
if __name__ == "__main__":
    # This block runs only when you execute this script directly

    # Optional: If you use a .env file to store your API key,
    # you need to install and use python-dotenv
    # pip install python-dotenv
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("Loaded .env file.")
    except ImportError:
        print(".env file not loaded. Make sure 'python-dotenv' is installed if you use it.")

    # 1. Create an instance of the agent
    #    It will automatically try to find the 'SUNO_API_KEY'
    #    from your environment variables.
    agent = CreateSongAgent()

    # 2. Check if the agent found the API key before proceeding
    if agent.api_key:

        # 3. Define the path to your *local* instrumental file
        #    *** IMPORTANT: REPLACE THIS WITH YOUR ACTUAL FILE PATH ***
        my_local_mp3 = r"C:\Users\masee\Downloads\my beat i made.mp3"
        # e.g., "C:/Users/MyUser/Music/instrumental.mp3" (Windows)
        # e.g., "/Users/MyUser/Music/instrumental.mp3" (Mac/Linux)
        # e.g., "./instrumental.mp3" (if it's in the same folder)

        # 4. Define the prompt for the vocals
        song_prompt = "A slow, soulful vo cal melody about walking in the rain."

        # 5. Call the method!
        agent.send_request(
            song_description=song_prompt,
            local_file_path=my_local_mp3
        )
    else:
        print("Please set the SUNO_API_KEY environment variable to run the example.")

# =====================================================
# MAIN PIPELINE
# =====================================================
class SongPipeline:
    def __init__(self, gemini_api_key=None):
        self.preprocess_agent = PreProcessAgent()
        self.lyric_gen_agent = LyricGenerationAgent(api_key=gemini_api_key)
        self.voice_synth_agent = VoiceSynthAgent(gemini_api_key)
        self.aligner_agent = AlignerAgent()
        self.mixer_agent = MixerAgent()

    def run(self, song_path, theme, artist_name="Unknown Artist"):
        print("\n" + "=" * 60)
        print("AI SONG PIPELINE STARTED")
        print("=" * 60)



        preprocess = self.preprocess_agent.process(song_path)
        lyrics_data = preprocess["lyrics_data"]

        rewritten = self.lyric_gen_agent.process(lyrics_data, theme)
        synth_vocals = self.voice_synth_agent.process(rewritten, artist_name=artist_name)
        aligned = self.aligner_agent.process(synth_vocals, lyrics_data)
        final = self.mixer_agent.process(preprocess["vocals_path"], preprocess["instrumental_path"], f"{Path(song_path).stem}_remix")
        

        print("\n✓ PIPELINE COMPLETE.")
        return final


# =====================================================
# ENTRY POINT
# =====================================================
def main():
    parser = argparse.ArgumentParser(description="AI Song Pipeline")
    parser.add_argument("--song", required=True)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--artist", default="Unknown Artist")
    args = parser.parse_args()

    pipeline = SongPipeline()
    output = pipeline.run(args.song, args.theme, args.artist)
    print(f"\nOutput saved to: {output}")


if __name__ == "__main__":
    sys.exit(main())
