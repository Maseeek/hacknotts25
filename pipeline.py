# #!/usr/bin/env python3
# """
# AI Song Pipeline - Transforms songs with AI-generated lyrics
# """

# import argparse
# import os
# import sys
# from pathlib import Path
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()


# class PreProcessAgent:
#     """
#     Pre-process Agent: Separates vocals from instrumental and extracts lyrics with timing
#     Uses Spleeter for separation and Whisper for transcription
#     """

#     def __init__(self):
#         self.output_dir = Path("output")
#         self.output_dir.mkdir(exist_ok=True)

    
#     def transcribe_lyrics(self, vocals_path):
#         """
#         Transcribe lyrics and timing using Whisper
#         Returns lyrics with word-level timestamps
#         """
#         print("[Pre-Process Agent] Transcribing lyrics with timing...")

#         try:
#             import whisper

#             # Load Whisper model (using base model for balance of speed/accuracy)
#             model = whisper.load_model("base")

#             # Transcribe with word-level timestamps
#             result = model.transcribe(vocals_path, word_timestamps=True)

#             # Extract lyrics and timing information
#             lyrics_data = {
#                 'text': result['text'],
#                 'segments': result['segments'],
#                 'language': result['language']
#             }

#             print(f"  ✓ Transcribed {len(result['segments'])} segments")
#             print(f"  ✓ Language: {result['language']}")
#             print(f"  ✓ Full text: {result['text'][:100]}...")

#             return lyrics_data

#         except Exception as e:
#             print(f"  ✗ Error during transcription: {e}")
#             raise

#     def process(self, song_path):
#         """
#         Main processing pipeline
#         """
#         print("\n" + "=" * 60)
#         print("STAGE 1: PRE-PROCESSING")
#         print("=" * 60)

#         # Separate audio
#         vocals_path, instrumental_path = self.separate_audio(song_path)

#         # Transcribe lyrics
#         lyrics_data = self.transcribe_lyrics(vocals_path)
#         return {
#             'vocals_path': vocals_path,
#             'instrumental_path': instrumental_path,
#             'lyrics_data': lyrics_data
#         }


# class LyricGenerationAgent:
#     """
#     Lyric Generation Agent: Rewrites lyrics to match a theme using Google Gemini
#     """

#     def __init__(self, api_key=None):
#         # This logic is correct: it tries the passed 'api_key' first,
#         # then falls back to the environment variable.
#         self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
#         if not self.api_key:
#             print("  ⚠ Warning: No Gemini API key found.")
#             print("     → Set GEMINI_API_KEY in your .env file")
#             print("     → Run 'python test_api_key.py' to verify your setup")
#         elif self.api_key == "put-key-here":
#             print("  ⚠ Warning: GEMINI_API_KEY is set to placeholder value.")
#             print("     → Update your .env file with a real API key")
#             print("     → Run 'python test_api_key.py' to verify your setup")
    
#     def rewrite_lyrics(self, original_lyrics, theme):
#         """
#         Rewrite lyrics to match the given theme using Google Gemini
#         """
#         print("\n" + "=" * 60)
#         print("STAGE 2: LYRIC GENERATION")
#         print("=" * 60)
#         print(f"[Lyric Gen Agent] Rewriting lyrics with theme: {theme}")

#         if not self.api_key:
#             print("  ✗ Cannot rewrite lyrics without API key")
#             return original_lyrics  # Returns original lyrics as a fallback

#         try:
#             import google.generativeai as genai

#             genai.configure(api_key=self.api_key)

#             # Create Gemini model
#             model = genai.GenerativeModel('gemini-pro')

#             # Create prompt for lyric rewriting
#             prompt = f"""You are a creative lyricist. Rewrite the following song lyrics to match the theme: "{theme}"

# Original lyrics:
# {original_lyrics['text']}

# Requirements:
# - Maintain the same structure and rhythm
# - Keep similar number of syllables per line
# - Make it fit the theme "{theme}"
# - Keep it creative and engaging

# Provide only the rewritten lyrics, no explanations."""

#             response = model.generate_content(prompt)

#             # Validate response contains text
#             if not response or not hasattr(response, 'text') or not response.text:
#                 raise ValueError("Gemini API returned empty or invalid response")

#             new_lyrics = response.text.strip()

#             print(f"  ✓ Generated new lyrics ({len(new_lyrics)} characters)")
#             print(f"  ✓ Preview: {new_lyrics[:100]}...")

#             return {
#                 'original': original_lyrics,
#                 'rewritten': new_lyrics,
#                 'theme': theme
#             }

#         except Exception as e:
#             print(f"  ✗ Error during lyric generation: {e}")
#             print("  → Returning original lyrics")
#             # Return the original lyrics in the *same format* as the success case
#             return {
#                 'original': original_lyrics,
#                 'rewritten': original_lyrics['text'],  # Use original text as rewritten
#                 'theme': theme
#             }

#     def process(self, lyrics_data, theme):
#         """
#         Main processing for lyric generation
#         """
#         return self.rewrite_lyrics(lyrics_data, theme)


# class VoiceSynthAgent:
#     """
#     Voice Synthesis Agent: Placeholder for future voice synthesis implementation
#     Would use TTS/voice cloning to generate new vocals
#     """

#     def __init__(self):
#         pass

#     def synthesize_voice(self, lyrics, reference_vocals_path):
#         """
#         Placeholder: Synthesize new vocals from lyrics
#         In a full implementation, this would use TTS or voice cloning
#         """
#         print("\n" + "=" * 60)
#         print("STAGE 3: VOICE SYNTHESIS")
#         print("=" * 60)
#         print("[Voice Synth Agent] Voice synthesis placeholder")
#         print("  ⚠ This stage is not yet implemented")
#         print("  → In the future, this would:")
#         print("     - Analyze the reference vocal characteristics")
#         print("     - Use TTS/voice cloning to generate new vocals")
#         print("     - Match the prosody and style of the original")
#         print("  → For now, returning original vocals path")

#         # This placeholder passes the *original* vocals path forward


#         return reference_vocals_path

#     def process(self, lyrics_data, vocals_path):
#         """
#         Main processing for voice synthesis
#         """
#         return self.synthesize_voice(lyrics_data, vocals_path)


# class AlignerAgent:
#     """
#     Aligner Agent: Placeholder for DTW-based audio alignment
#     Would use Dynamic Time Warping to align new vocals with timing
#     """

#     def __init__(self):
#         pass

#     def align_audio(self, synthesized_vocals_path, original_timing):
#         """
#         Placeholder: Align synthesized vocals using DTW
#         In a full implementation, this would use fastdtw for alignment
#         """
#         print("\n" + "=" * 60)
#         print("STAGE 4: ALIGNMENT")
#         print("=" * 60)
#         print("[Aligner Agent] Audio alignment placeholder (DTW)")
#         print("  ⚠ This stage is not yet implemented")
#         print("  → In the future, this would:")
#         print("     - Use Dynamic Time Warping (DTW) via fastdtw")
#         print("     - Align synthesized vocals to match original timing")
#         print("     - Ensure syllables match the beat")
#         print("  → For now, returning vocals path unchanged")

#         # This placeholder passes the vocals path forward
#         return synthesized_vocals_path

#     def process(self, vocals_path, timing_data):
#         """
#         Main processing for alignment
#         """
#         return self.align_audio(vocals_path, timing_data)


# class MixerAgent:
#     """
#     Mixer Agent: Overlays vocals on instrumental using pydub
#     """

#     def __init__(self):
#         self.output_dir = Path("output")
#         self.output_dir.mkdir(exist_ok=True)

#     def mix_tracks(self, vocals_path, instrumental_path, output_name="final_mix"):
#         """
#         Mix vocals and instrumental together using pydub
#         """
#         print("\n" + "=" * 60)
#         print("STAGE 5: MIXING")
#         print("=" * 60)
#         print("[Mixer Agent] Mixing vocals and instrumental...")

#         try:
#             from pydub import AudioSegment

#             # Load audio files
#             print("  → Loading vocals...")
#             vocals = AudioSegment.from_wav(vocals_path)

#             print("  → Loading instrumental...")
#             instrumental = AudioSegment.from_wav(instrumental_path)

#             # Ensure both tracks are the same length
#             # Trim or pad as needed
#             if len(vocals) > len(instrumental):
#                 vocals = vocals[:len(instrumental)]
#             elif len(instrumental) > len(vocals):
#                 instrumental = instrumental[:len(vocals)]

#             print(f"  → Track length: {len(vocals) / 1000:.2f} seconds")

#             # Mix tracks by overlaying
#             print("  → Overlaying tracks...")
#             mixed = vocals.overlay(instrumental)

#             # Export final mix
#             output_path = self.output_dir / f"{output_name}.wav"
#             print(f"  → Exporting to {output_path}...")
#             mixed.export(str(output_path), format="wav")

#             print(f"  ✓ Final mix saved to: {output_path}")

#             return str(output_path)

#         except Exception as e:
#             print(f"  ✗ Error during mixing: {e}")
#             raise

#     def process(self, vocals_path, instrumental_path, output_name="final_mix"):
#         """
#         Main processing for mixing
#         """
#         return self.mix_tracks(vocals_path, instrumental_path, output_name)


# class SongPipeline:
#     """
#     Main pipeline orchestrator that runs all 5 agents in sequence
#     """

#     # <--- FIX: Renamed 'openai_api_key' to 'gemini_api_key' for clarity
#     def __init__(self, gemini_api_key=None):
#         self.preprocess_agent = PreProcessAgent()
#         # <--- FIX: Pass the correctly named key
#         self.lyric_gen_agent = LyricGenerationAgent(api_key=gemini_api_key)
#         self.voice_synth_agent = VoiceSynthAgent()
#         self.aligner_agent = AlignerAgent()
#         self.mixer_agent = MixerAgent()

#     def run(self, song_path, theme):
#         """
#         Run the full AI song transformation pipeline
#         """
#         print("\n" + "=" * 60)
#         print("AI SONG PIPELINE")
#         print("=" * 60)
#         print(f"Input song: {song_path}")
#         print(f"Theme: {theme}")
#         print("=" * 60)

#         try:
#             # Stage 1: Pre-process (separation + transcription)
#             preprocess_result = self.preprocess_agent.process(song_path)

#             # Stage 2: Lyric Generation (rewrite to theme)
#             new_lyrics_data = self.lyric_gen_agent.process(
#                 preprocess_result['lyrics_data'],
#                 theme
#             )

#             # Stage 3: Voice Synthesis (placeholder)
#             # This stage currently just passes the *original* vocals path
#             synthesized_vocals = self.voice_synth_agent.process(
#                 new_lyrics_data,  # Pass new lyrics for future use
#                 preprocess_result['vocals_path']
#             )

#             # Stage 4: Alignment (placeholder)
#             # This stage currently just passes the *original* vocals path
#             aligned_vocals = self.aligner_agent.process(
#                 synthesized_vocals,
#                 preprocess_result['lyrics_data']  # Pass original timing
#             )

#             # Stage 5: Mixing (overlay *original* vocals on instrumental)
#             song_name = Path(song_path).stem
#             output_name = f"{song_name}_themed_{theme.replace(' ', '_')}"
#             final_output = self.mixer_agent.process(
#                 aligned_vocals,
#                 preprocess_result['instrumental_path'],
#                 output_name
#             )

#             print("\n" + "=" * 60)
#             print("PIPELINE COMPLETE!")
#             print("=" * 60)
#             print(f"✓ Final output: {final_output}")

#             # If lyrics were rewritten, print a note that they weren't used in the audio
#             if new_lyrics_data['rewritten'] != new_lyrics_data['original']['text']:
#                 print("\nNOTE: New lyrics were generated but not synthesized.")
#                 print("The final audio mix still uses the *original* vocals.")
#                 print("Generated lyrics preview:")
#                 print(f"'{new_lyrics_data['rewritten'][:150]}...'")

#             print("=" * 60 + "\n")

#             return final_output

#         except Exception as e:
#             print(f"\n✗ Pipeline failed: {e}")
#             raise


# def main():
#     """
#     Main entry point with argument parsing
#     """

#     # <--- ADD THIS LINE TO LOAD .env FILE AT THE START
#     load_dotenv()

#     parser = argparse.ArgumentParser(
#         description="AI Song Pipeline - Transform songs with AI-generated themed lyrics",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Examples:
#   python pipeline.py --song input.mp3 --theme "space exploration"
#   python pipeline.py --song my_song.wav --theme "medieval fantasy"

# Environment Variables:
#   GEMINI_API_KEY - Google Gemini API key for lyric generation (required for full functionality)
#         """
#     )

#     parser.add_argument(
#         '--song',
#         type=str,
#         required=True,
#         help='Path to the input song file (MP3, WAV, etc.)'
#     )

#     parser.add_argument(
#         '--theme',
#         type=str,
#         required=True,
#         help='Theme for the rewritten lyrics (e.g., "space exploration", "medieval fantasy")'
#     )

#     parser.add_argument(
#         '--api-key',
#         type=str,
#         default=None,
#         help='Google Gemini API key (alternatively set GEMINI_API_KEY env var)'
#     )

#     args = parser.parse_args()

#     # Validate song file exists
#     if not os.path.exists(args.song):
#         print(f"Error: Song file not found: {args.song}")
#         sys.exit(1)

#     # Create and run pipeline
#     # <--- FIX: Use the corrected 'gemini_api_key' argument name
#     pipeline = SongPipeline(gemini_api_key=args.api_key)

#     try:
#         output_file = pipeline.run(args.song, args.theme)
#         print(f"\n✓ Success! Output saved to: {output_file}")
#         return 0
#     except Exception as e:
#         print(f"\n✗ Pipeline failed: {e}")
#         return 1


# if __name__ == "__main__":
#     sys.exit(main())




#!/usr/bin/env python3
"""
AI Song Pipeline - Transforms songs with AI-generated lyrics
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class PreProcessAgent:
    """
    Handles audio preprocessing — communicates with the Spleeter Flask microservice
    to separate vocals and instrumentals.
    """

    def __init__(self, spleeter_service_url="http://127.0.0.1:5001/split"):
        self.spleeter_service_url = spleeter_service_url
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def separate_audio(self, song_path):
        """
        Sends a POST request to the Flask Spleeter service to split the song.
        Returns paths to the generated vocals and instrumental files.
        """
        print("[Pre-Process Agent] Requesting audio separation from Spleeter service...")

        try:
            with open(song_path, 'rb') as f:
                files = {'file': (Path(song_path).name, f, 'audio/mpeg')}
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


class LyricGenerationAgent:
    """
    Lyric Generation Agent: Rewrites lyrics to match a theme using Google Gemini
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            print("  ⚠ Warning: No Gemini API key found.")
            print("     → Set GEMINI_API_KEY in your .env file")
            print("     → Run 'python test_api_key.py' to verify your setup")
        elif self.api_key == "put-key-here":
            print("  ⚠ Warning: GEMINI_API_KEY is set to placeholder value.")
            print("     → Update your .env file with a real API key")
            print("     → Run 'python test_api_key.py' to verify your setup")

    def rewrite_lyrics(self, original_lyrics, theme):
        """
        Rewrite lyrics to match the given theme using Google Gemini
        """
        print("\n" + "=" * 60)
        print("STAGE 2: LYRIC GENERATION")
        print("=" * 60)
        print(f"[Lyric Gen Agent] Rewriting lyrics with theme: {theme}")

        if not self.api_key:
            print("  ✗ Cannot rewrite lyrics without API key")
            return original_lyrics

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)

            # Create Gemini model
            model = genai.GenerativeModel('gemini-pro')

            # Create prompt for lyric rewriting
            prompt = f"""You are a creative lyricist. Rewrite the following song lyrics to match the theme: "{theme}"

Original lyrics:
{original_lyrics['text']}

Requirements:
- Maintain the same structure and rhythm
- Keep similar number of syllables per line
- Make it fit the theme "{theme}"
- Keep it creative and engaging

Provide only the rewritten lyrics, no explanations."""

            response = model.generate_content(prompt)

            if not response or not hasattr(response, 'text') or not response.text:
                raise ValueError("Gemini API returned empty or invalid response")

            new_lyrics = response.text.strip()

            print(f"  ✓ Generated new lyrics ({len(new_lyrics)} characters)")
            print(f"  ✓ Preview: {new_lyrics[:100]}...")

            return {
                'original': original_lyrics,
                'rewritten': new_lyrics,
                'theme': theme
            }

        except Exception as e:
            print(f"  ✗ Error during lyric generation: {e}")
            print("  → Returning original lyrics")
            return {
                'original': original_lyrics,
                'rewritten': original_lyrics['text'],
                'theme': theme
            }

    def process(self, lyrics_data, theme):
        """
        Main processing for lyric generation
        """
        return self.rewrite_lyrics(lyrics_data, theme)


class VoiceSynthAgent:
    """
    Voice Synthesis Agent: Uses Gemini to analyze artist vocal characteristics
    and intelligently select the best ElevenLabs voice for synthesis.
    """

    def __init__(self, gemini_api_key=None, elevenlabs_api_key=None):
        # Setup API keys
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.elevenlabs_api_key = elevenlabs_api_key or os.environ.get("ELEVENLABS_API_KEY")

        if not self.gemini_api_key:
            print("  ⚠ Warning: No Gemini API key found for voice analysis.")

        if not self.elevenlabs_api_key:
            print("  ⚠ Warning: No ElevenLabs API key found for voice synthesis.")

        # Initialize Gemini (Gemini 2.5)
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                print("  ✓ Gemini initialized")
            except Exception as e:
                print(f"  ✗ Could not initialize Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None

        # Initialize ElevenLabs client
        if self.elevenlabs_api_key:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)
                print("  ✓ ElevenLabs initialized")
            except Exception as e:
                print(f"  ✗ Could not initialize ElevenLabs: {e}")
                self.elevenlabs_client = None
        else:
            self.elevenlabs_client = None

    # --------------------------------------------------
    # 1️⃣ Get artist voice description via Gemini
    # --------------------------------------------------
    def get_voice_description(self, artist_name):
        if not self.gemini_model:
            return f"Voice similar to {artist_name}"

        print(f"\n[Voice Synth Agent] Analyzing vocal characteristics of {artist_name}...")

        prompt = f"""
        Describe the vocal characteristics of {artist_name} in detail for voice synthesis purposes.
        DO NOT repeat the artist's name. Include:

        1. Voice type (tenor, baritone, bass, etc.)
        2. Tone quality (warm, raspy, smooth, breathy, crisp, etc.)
        3. Vocal range and register
        4. Distinctive vocal techniques or styles
        5. Emotional delivery style (laid-back, aggressive, melodic, etc.)
        6. Unique vocal quirks or characteristics
        7. Typical vocal effects (reverb, autotune level, etc.)

        Keep it concise but technical enough for AI voice synthesis.
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            description = response.text.strip()
            print(f"  ✓ Voice description generated\n{description}\n")
            return description
        except Exception as e:
            print(f"  ✗ Error generating voice description: {e}")
            return f"Voice similar to {artist_name}, expressive and clear"

    # --------------------------------------------------
    # 2️⃣ Get ElevenLabs voice list
    # --------------------------------------------------
    def get_available_voices(self):
        if not self.elevenlabs_client:
            return []
        try:
            response = self.elevenlabs_client.voices.get_all()
            return response.voices
        except Exception as e:
            print(f"  ✗ Error fetching voices: {e}")
            return []

    # --------------------------------------------------
    # 3️⃣ Match best ElevenLabs voice via Gemini
    # --------------------------------------------------
    def get_best_voice_match(self, voice_description, artist_name):
        if not self.gemini_model:
            return "pNInz6obpgDQGcFmaJgB"  # Default Adam voice ID

        print(f"[Voice Synth Agent] Selecting best voice match for {artist_name}...")

        available_voices = self.get_available_voices()
        if not available_voices:
            print("  ⚠ No voices available, using default.")
            return "pNInz6obpgDQGcFmaJgB"

        voice_list = [
            f"- {v.name} (ID: {v.voice_id})"
            + (f" - {v.description}" if getattr(v, "description", None) else "")
            for v in available_voices
        ]

        prompt = f"""
        Given the following vocal description for {artist_name}:

        {voice_description}

        Which of these ElevenLabs voices would best match?
        Consider tone, range, style, and emotional delivery.

        Available voices:
        {chr(10).join(voice_list)}

        Return ONLY the exact voice name (e.g., "Adam" or "Rachel"), no explanation.
        """

        try:
            response = self.gemini_model.generate_content(prompt)
            voice_name = response.text.strip().replace('"', '').replace("'", '')

            for v in available_voices:
                if v.name.lower() == voice_name.lower():
                    print(f"  ✓ Selected voice: {v.name} (ID: {v.voice_id})")
                    return v.voice_id

            print(f"  ⚠ Voice '{voice_name}' not found, using default.")
            return "pNInz6obpgDQGcFmaJgB"

        except Exception as e:
            print(f"  ✗ Error selecting voice: {e}")
            return "pNInz6obpgDQGcFmaJgB"

    # --------------------------------------------------
    # 4️⃣ Generate vocals with ElevenLabs
    # --------------------------------------------------
    def synthesize_voice(self, lyrics, artist_name=None):
        print("\n" + "=" * 60)
        print("STAGE 3: VOICE SYNTHESIS")
        print("=" * 60)

        if not self.elevenlabs_client:
            print("  ✗ ElevenLabs not initialized")
            return None

        if artist_name:
            voice_description = self.get_voice_description(artist_name)
            selected_voice_id = self.get_best_voice_match(voice_description, artist_name)
        else:
            selected_voice_id = "pNInz6obpgDQGcFmaJgB"
            print("  → Using default voice")

        print(f"  → Generating vocals with ID: {selected_voice_id}")

        try:
            audio_stream = self.elevenlabs_client.generate(
                text=lyrics,
                voice=selected_voice_id,
                model="eleven_multilingual_v2",
            )

            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "synthesized_vocals.mp3"

            audio_bytes = b"".join(audio_stream)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            print(f"  ✓ Vocals generated and saved to: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"  ✗ Error during synthesis: {e}")
            return None


    def process(self, lyrics_data, vocals_path=None, artist_name=None):
        """
        Called by main pipeline.
        """
        if isinstance(lyrics_data, dict):
            lyrics = lyrics_data.get("rewritten") or lyrics_data.get("original", {}).get("text", "")
        else:
            lyrics = str(lyrics_data)

        return self.synthesize_voice(lyrics, artist_name)


class AlignerAgent:
    """
    Aligner Agent: Placeholder for DTW-based audio alignment
    Would use Dynamic Time Warping to align new vocals with timing
    """

    def __init__(self):
        pass

    def align_audio(self, synthesized_vocals_path, original_timing):
        """
        Placeholder: Align synthesized vocals using DTW
        In a full implementation, this would use fastdtw for alignment
        """
        print("\n" + "=" * 60)
        print("STAGE 4: ALIGNMENT")
        print("=" * 60)
        print("[Aligner Agent] Audio alignment placeholder (DTW)")
        print("  ⚠ This stage is not yet implemented")
        print("  → In the future, this would:")
        print("     - Use Dynamic Time Warping (DTW) via fastdtw")
        print("     - Align synthesized vocals to match original timing")
        print("     - Ensure syllables match the beat")
        print("  → For now, returning vocals path unchanged")

        return synthesized_vocals_path

    def process(self, vocals_path, timing_data):
        """
        Main processing for alignment
        """
        return self.align_audio(vocals_path, timing_data)


class MixerAgent:
    """
    Mixer Agent: Overlays vocals on instrumental using pydub
    """

    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def mix_tracks(self, vocals_path, instrumental_path, output_name="final_mix"):
        """
        Mix vocals and instrumental together using pydub
        """
        print("\n" + "=" * 60)
        print("STAGE 5: MIXING")
        print("=" * 60)
        print("[Mixer Agent] Mixing vocals and instrumental...")

        try:
            from pydub import AudioSegment

            # Load audio files
            print("  → Loading vocals...")
            vocals = AudioSegment.from_wav(vocals_path)

            print("  → Loading instrumental...")
            instrumental = AudioSegment.from_wav(instrumental_path)

            # Ensure both tracks are the same length
            if len(vocals) > len(instrumental):
                vocals = vocals[:len(instrumental)]
            elif len(instrumental) > len(vocals):
                instrumental = instrumental[:len(vocals)]

            print(f"  → Track length: {len(vocals) / 1000:.2f} seconds")

            # Mix tracks by overlaying
            print("  → Overlaying tracks...")
            mixed = vocals.overlay(instrumental)

            # Export final mix
            output_path = self.output_dir / f"{output_name}.wav"
            print(f"  → Exporting to {output_path}...")
            mixed.export(str(output_path), format="wav")

            print(f"  ✓ Final mix saved to: {output_path}")

            return str(output_path)

        except Exception as e:
            print(f"  ✗ Error during mixing: {e}")
            raise

    def process(self, vocals_path, instrumental_path, output_name="final_mix"):
        """
        Main processing for mixing
        """
        return self.mix_tracks(vocals_path, instrumental_path, output_name)


class SongPipeline:
    """
    Main pipeline orchestrator that runs all 5 agents in sequence
    """

    def __init__(self, gemini_api_key=None, elevenlabs_api_key=None, artist_name=None):
        self.preprocess_agent = PreProcessAgent()
        self.lyric_gen_agent = LyricGenerationAgent(api_key=gemini_api_key)
        self.voice_synth_agent = VoiceSynthAgent(
            gemini_api_key=gemini_api_key,
            elevenlabs_api_key=elevenlabs_api_key
        )
        self.aligner_agent = AlignerAgent()
        self.mixer_agent = MixerAgent()
        self.artist_name = artist_name

    def run(self, song_path, theme):
        """
        Run the full AI song transformation pipeline
        """
        print("\n" + "=" * 60)
        print("AI SONG PIPELINE")
        print("=" * 60)
        print(f"Input song: {song_path}")
        print(f"Theme: {theme}")
        if self.artist_name:
            print(f"Artist voice style: {self.artist_name}")
        print("=" * 60)

        try:
            # Stage 1: Pre-process (separation + transcription)
            preprocess_result = self.preprocess_agent.process(song_path)

            # Stage 2: Lyric Generation (rewrite to theme)
            new_lyrics_data = self.lyric_gen_agent.process(
                preprocess_result['lyrics_data'],
                theme
            )

            # Stage 3: Voice Synthesis (with artist-based voice selection)
            synthesized_vocals = self.voice_synth_agent.process(
                new_lyrics_data,
                preprocess_result['vocals_path'],
                artist_name=self.artist_name
            )

            # Stage 4: Alignment (placeholder)
            aligned_vocals = self.aligner_agent.process(
                synthesized_vocals,
                preprocess_result['lyrics_data']
            )

            # Stage 5: Mixing
            song_name = Path(song_path).stem
            output_name = f"{song_name}_themed_{theme.replace(' ', '_')}"
            final_output = self.mixer_agent.process(
                aligned_vocals,
                preprocess_result['instrumental_path'],
                output_name
            )

            print("\n" + "=" * 60)
            print("PIPELINE COMPLETE!")
            print("=" * 60)
            print(f"✓ Final output: {final_output}")

            # Show what was done
            vocals_changed = synthesized_vocals != preprocess_result['vocals_path']
            if vocals_changed:
                print("\n✓ New AI-generated vocals were synthesized and mixed!")
                print(f"  Voice style based on: {self.artist_name or 'default'}")
            else:
                print("\nNOTE: Voice synthesis was not performed (missing API keys).")
                print("The final audio uses original vocals with rewritten lyrics shown below.")
            
            if new_lyrics_data['rewritten'] != new_lyrics_data['original']['text']:
                print("\n✓ New lyrics generated:")
                print(f"'{new_lyrics_data['rewritten'][:200]}...'")

            print("=" * 60 + "\n")

            return final_output

        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
            raise


def main():
    """
    Main entry point with argument parsing
    """
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="AI Song Pipeline - Transform songs with AI-generated themed lyrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --song input.mp3 --theme "space exploration" --artist "Drake"
  python pipeline.py --song my_song.wav --theme "medieval fantasy" --artist "J. Cole"

Environment Variables:
  GEMINI_API_KEY - Google Gemini API key (required for lyric generation and voice analysis)
  ELEVENLABS_API_KEY - ElevenLabs API key (required for voice synthesis)
        """
    )

    parser.add_argument(
        '--song',
        type=str,
        required=True,
        help='Path to the input song file (MP3, WAV, etc.)'
    )

    parser.add_argument(
        '--theme',
        type=str,
        required=True,
        help='Theme for the rewritten lyrics (e.g., "space exploration", "medieval fantasy")'
    )

    parser.add_argument(
        '--artist',
        type=str,
        default=None,
        help='Artist name to match voice style (e.g., "Drake", "J. Cole", "Kendrick Lamar")'
    )

    parser.add_argument(
        '--gemini-api-key',
        type=str,
        default=None,
        help='Google Gemini API key (alternatively set GEMINI_API_KEY env var)'
    )

    parser.add_argument(
        '--elevenlabs-api-key',
        type=str,
        default=None,
        help='ElevenLabs API key (alternatively set ELEVENLABS_API_KEY env var)'
    )

    args = parser.parse_args()

    # Validate song file exists
    if not os.path.exists(args.song):
        print(f"Error: Song file not found: {args.song}")
        sys.exit(1)

    # Create and run pipeline
    pipeline = SongPipeline(
        gemini_api_key=args.gemini_api_key,
        elevenlabs_api_key=args.elevenlabs_api_key,
        artist_name=args.artist
    )

    try:
        output_file = pipeline.run(args.song, args.theme)
        print(f"\n✓ Success! Output saved to: {output_file}")
        return 0
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())