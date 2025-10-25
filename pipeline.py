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
            Maintain the rhythm, syllable count, and flow.

            Original:
            {original_lyrics['text']}
            """

            response = model.generate_content(prompt)
            rewritten = response.text.strip() if response and hasattr(response, "text") else None

            if not rewritten:
                raise ValueError("Empty response from Gemini")

            print(f"  ✓ New lyrics generated."{rewritten})
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
    def process(self, vocals_path, timing_data):
        print("\n" + "=" * 60)
        print("STAGE 4: ALIGNMENT (Placeholder)")
        print("=" * 60)
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
