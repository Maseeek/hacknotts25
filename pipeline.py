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
    Pre-process Agent: Extracts lyrics with timing from audio
    
    NOTE: Audio separation (Spleeter) has been removed as it requires Python 3.8.
    This agent now only performs transcription using Whisper.
    
    For audio separation, use:
    1. A separate Python 3.8 environment with Spleeter
    2. Pre-separated audio files (vocals and instrumental)
    """

    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def separate_audio(self, song_path):
        """
        Separate vocals from instrumental using Spleeter
        
        NOTE: This functionality is disabled as Spleeter requires Python 3.8.
        This method will raise an error if called.
        """
        raise NotImplementedError(
            "Audio separation using Spleeter is not available in Python 3.12. "
            "The Spleeter library requires Python 3.8. "
            "\n\nTo use audio separation, you have two options:"
            "\n1. Run audio separation in a separate Python 3.8 environment with Spleeter installed"
            "\n2. Use pre-separated audio files (vocals and instrumental) instead"
            "\n\nIf you have pre-separated files, you can skip this step and provide "
            "the paths directly to the transcription step."
        )

    def transcribe_lyrics(self, vocals_path):
        """
        Transcribe lyrics and timing using Whisper
        Returns lyrics with word-level timestamps
        """
        print("[Pre-Process Agent] Transcribing lyrics with timing...")

        try:
            import whisper

            # Load Whisper model (using base model for balance of speed/accuracy)
            model = whisper.load_model("base")

            # Transcribe with word-level timestamps
            result = model.transcribe(vocals_path, word_timestamps=True)

            # Extract lyrics and timing information
            lyrics_data = {
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language']
            }

            print(f"  ✓ Transcribed {len(result['segments'])} segments")
            print(f"  ✓ Language: {result['language']}")
            print(f"  ✓ Full text: {result['text'][:100]}...")

            return lyrics_data

        except Exception as e:
            print(f"  ✗ Error during transcription: {e}")
            raise

    def process(self, song_path=None, vocals_path=None, instrumental_path=None):
        """
        Main processing pipeline
        
        Args:
            song_path: Path to song file (if using audio separation - NOT SUPPORTED)
            vocals_path: Path to pre-separated vocals file (required)
            instrumental_path: Path to pre-separated instrumental file (required)
        
        Note: Audio separation is no longer supported. You must provide 
              pre-separated vocals and instrumental files.
        """
        print("\n" + "=" * 60)
        print("STAGE 1: PRE-PROCESSING")
        print("=" * 60)

        # Check if pre-separated files are provided
        if vocals_path and instrumental_path:
            print("[Pre-Process Agent] Using pre-separated audio files...")
            print(f"  → Vocals: {vocals_path}")
            print(f"  → Instrumental: {instrumental_path}")
        elif song_path:
            # If only song_path is provided, try to call separate_audio
            # This will raise NotImplementedError with helpful message
            print("[Pre-Process Agent] Attempting audio separation...")
            vocals_path, instrumental_path = self.separate_audio(song_path)
        else:
            raise ValueError(
                "You must provide either:\n"
                "1. Pre-separated vocals_path and instrumental_path, OR\n"
                "2. A song_path (but audio separation is not available in Python 3.12)"
            )

        # Transcribe lyrics
        lyrics_data = self.transcribe_lyrics(vocals_path)
        
        return {
            'vocals_path': vocals_path,
            'instrumental_path': instrumental_path,
            'lyrics_data': lyrics_data
        }


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
    and intelligently select the best ElevenLabs voice for synthesis
    """

    def __init__(self, gemini_api_key=None, elevenlabs_api_key=None):
        # Setup Gemini API
        self.gemini_api_key = gemini_api_key or os.environ.get('GEMINI_API_KEY')
        self.elevenlabs_api_key = elevenlabs_api_key or os.environ.get('ELEVENLABS_API_KEY')
        
        if not self.gemini_api_key:
            print("  ⚠ Warning: No Gemini API key found for voice analysis.")
        
        if not self.elevenlabs_api_key:
            print("  ⚠ Warning: No ElevenLabs API key found for voice synthesis.")
        
        # Initialize Gemini if available
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"  ⚠ Could not initialize Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        # Initialize ElevenLabs if available
        if self.elevenlabs_api_key:
            try:
                from elevenlabs import set_api_key
                set_api_key(self.elevenlabs_api_key)
            except Exception as e:
                print(f"  ⚠ Could not initialize ElevenLabs: {e}")

    def get_voice_description(self, artist_name):
        """
        Use Gemini to generate a detailed voice description based on artist name
        """
        if not self.gemini_model:
            return f"Voice similar to {artist_name}"
        
        print(f"[Voice Synth Agent] Analyzing vocal characteristics of {artist_name}...")
        
        prompt = f"""Describe the vocal characteristics of {artist_name} in detail for voice synthesis purposes. Include:

1. Voice type (tenor, baritone, bass, etc.)
2. Tone quality (warm, raspy, smooth, breathy, crisp, etc.)
3. Vocal range and register
4. Distinctive vocal techniques or styles
5. Emotional delivery style (laid-back, aggressive, melodic, etc.)
6. Any unique vocal quirks or characteristics
7. Typical vocal effects (reverb, autotune level, etc.)

Keep it concise but technical enough for voice synthesis. Format as a single detailed paragraph."""

        try:
            response = self.gemini_model.generate_content(prompt)
            description = response.text.strip()
            print(f"  ✓ Voice description generated")
            return description
        except Exception as e:
            print(f"  ✗ Error generating voice description: {e}")
            return f"Voice similar to {artist_name}, expressive and clear"

    def get_available_voices(self):
        """
        Get list of available ElevenLabs voices
        """
        try:
            from elevenlabs import voices
            available_voices = voices()
            return available_voices
        except Exception as e:
            print(f"  ✗ Error fetching voices: {e}")
            return []

    def get_best_voice_match(self, voice_description, artist_name):
        """
        Use Gemini to intelligently select the best ElevenLabs voice based on description
        """
        if not self.gemini_model:
            return "Adam"
        
        print(f"[Voice Synth Agent] Selecting best voice match for {artist_name}...")
        
        # Get available voices
        available_voices = self.get_available_voices()
        
        if not available_voices:
            print("  ⚠ No voices available, using default 'Adam'")
            return "Adam"
        
        # Format voice list for Gemini
        voice_list = []
        for v in available_voices:
            voice_info = f"- {v.name}"
            if hasattr(v, 'labels') and v.labels:
                labels = ', '.join([f"{k}: {val}" for k, val in v.labels.items()])
                voice_info += f" ({labels})"
            if hasattr(v, 'description') and v.description:
                voice_info += f" - {v.description}"
            voice_list.append(voice_info)
        
        prompt = f"""You are a voice matching expert. Given this vocal description for {artist_name}:

{voice_description}

Which of these ElevenLabs voices would be the BEST match? Consider:
- Voice type and gender
- Tone quality and character
- Age and maturity
- Accent and style
- Overall similarity to the artist

Available voices:
{chr(10).join(voice_list)}

Return ONLY the exact voice name (e.g., "Adam" or "Rachel"), nothing else. No explanations."""

        try:
            response = self.gemini_model.generate_content(prompt)
            voice_name = response.text.strip().replace('"', '').replace("'", '')
            
            # Verify the voice exists
            voice_names = [v.name for v in available_voices]
            if voice_name in voice_names:
                print(f"  ✓ Selected voice: {voice_name}")
                return voice_name
            else:
                print(f"  ⚠ Voice '{voice_name}' not found, using 'Adam'")
                return "Adam"
                
        except Exception as e:
            print(f"  ✗ Error selecting voice: {e}")
            return "Adam"

    def synthesize_voice(self, lyrics, reference_vocals_path, artist_name=None, voice_description=None):
        """
        Synthesize new vocals from lyrics using AI-selected voice
        """
        print("\n" + "=" * 60)
        print("STAGE 3: VOICE SYNTHESIS")
        print("=" * 60)
        
        # Check if we have the necessary API keys
        if not self.elevenlabs_api_key:
            print("[Voice Synth Agent] Voice synthesis not available (no ElevenLabs API key)")
            print("  ⚠ Returning original vocals path")
            return reference_vocals_path
        
        # Get voice description from Gemini if artist name provided
        if artist_name and not voice_description:
            voice_description = self.get_voice_description(artist_name)
            print(f"\n[Voice Profile for {artist_name}]")
            print(f"{voice_description}\n")
        elif voice_description:
            print(f"\n[Voice Profile]")
            print(f"{voice_description}\n")
        else:
            voice_description = "Clear, expressive male voice"
            print(f"\n[Voice Profile] Using default couldn't generate new description: {voice_description}\n")
        
        # Use Gemini to intelligently select the best voice
        if artist_name and self.gemini_model:
            selected_voice = self.get_best_voice_match(voice_description, artist_name)
        else:
            selected_voice = "Adam"
            print(f"[Voice Synth Agent] Using default voice: {selected_voice}")
        
        # Generate vocals with AI-selected voice
        print(f"[Voice Synth Agent] Generating vocals with {selected_voice}...")
        
        try:
            from elevenlabs import generate
            
            audio = generate(
                text=lyrics,
                voice=selected_voice,
                model="eleven_multilingual_v2"
            )
            
            # Save the audio
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "new_vocals_raw.wav"
            
            with open(output_path, "wb") as f:
                f.write(audio)
            
            print(f"  ✓ Vocals generated successfully")
            print(f"  ✓ Saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"  ✗ Error during voice synthesis: {e}")
            print(f"  → Returning original vocals path")
            return reference_vocals_path

    def process(self, lyrics_data, vocals_path, artist_name=None):
        """
        Main processing for voice synthesis
        
        Args:
            lyrics_data: Dictionary containing lyrics (e.g., {'rewritten': '...', 'original': ...})
            vocals_path: Path to reference vocals
            artist_name: Name of artist to match voice style (optional)
            
        Returns:
            Path to synthesized vocals file
        """
        # Extract lyrics from data
        if isinstance(lyrics_data, dict):
            # Use rewritten lyrics if available, otherwise original
            lyrics = lyrics_data.get('rewritten', lyrics_data.get('original', {}).get('text', ''))
        else:
            lyrics = str(lyrics_data)
        
        return self.synthesize_voice(
            lyrics=lyrics,
            reference_vocals_path=vocals_path,
            artist_name=artist_name
        )


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

    def run(self, song_path=None, theme=None, vocals_path=None, instrumental_path=None):
        """
        Run the full AI song transformation pipeline
        
        Args:
            song_path: Path to song file (optional, for display purposes)
            theme: Theme for lyric rewriting (required)
            vocals_path: Path to pre-separated vocals file (required)
            instrumental_path: Path to pre-separated instrumental file (required)
        
        Note: Audio separation is no longer supported. You must provide
              pre-separated vocals and instrumental files.
        """
        print("\n" + "=" * 60)
        print("AI SONG PIPELINE")
        print("=" * 60)
        if song_path:
            print(f"Input song: {song_path}")
        if vocals_path:
            print(f"Vocals: {vocals_path}")
        if instrumental_path:
            print(f"Instrumental: {instrumental_path}")
        print(f"Theme: {theme}")
        if self.artist_name:
            print(f"Artist voice style: {self.artist_name}")
        print("=" * 60)

        if not theme:
            raise ValueError("Theme is required for lyric rewriting")

        try:
            # Stage 1: Pre-process (transcription only, no separation)
            preprocess_result = self.preprocess_agent.process(
                song_path=song_path,
                vocals_path=vocals_path,
                instrumental_path=instrumental_path
            )

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
            if song_path:
                song_name = Path(song_path).stem
            elif vocals_path:
                song_name = Path(vocals_path).stem.replace('_vocals', '').replace('-vocals', '')
            else:
                song_name = "output"
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
        description="AI Song Pipeline - Transform songs with AI-generated themed lyrics (Python 3.12+)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using pre-separated audio files (recommended):
  python pipeline.py --vocals vocals.wav --instrumental instrumental.wav --theme "space exploration"
  
  # With artist voice style:
  python pipeline.py --vocals vocals.wav --instrumental instrumental.wav --theme "medieval fantasy" --artist "Drake"

Note: Audio separation (Spleeter) is not available in Python 3.12.
You must provide pre-separated vocals and instrumental files using --vocals and --instrumental.

Environment Variables:
  GEMINI_API_KEY - Google Gemini API key (required for lyric generation and voice analysis)
  ELEVENLABS_API_KEY - ElevenLabs API key (required for voice synthesis)
        """
    )

    parser.add_argument(
        '--vocals',
        type=str,
        required=True,
        help='Path to pre-separated vocals file (WAV format recommended)'
    )

    parser.add_argument(
        '--instrumental',
        type=str,
        required=True,
        help='Path to pre-separated instrumental file (WAV format recommended)'
    )

    parser.add_argument(
        '--song',
        type=str,
        default=None,
        help='(Optional) Path to original song file for reference/display purposes'
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

    # Validate required files exist
    if not os.path.exists(args.vocals):
        print(f"Error: Vocals file not found: {args.vocals}")
        sys.exit(1)
    
    if not os.path.exists(args.instrumental):
        print(f"Error: Instrumental file not found: {args.instrumental}")
        sys.exit(1)
    
    if args.song and not os.path.exists(args.song):
        print(f"Warning: Song file not found: {args.song} (optional, ignoring)")
        args.song = None

    # Create and run pipeline
    pipeline = SongPipeline(
        gemini_api_key=args.gemini_api_key,
        elevenlabs_api_key=args.elevenlabs_api_key,
        artist_name=args.artist
    )

    try:
        output_file = pipeline.run(
            song_path=args.song,
            theme=args.theme,
            vocals_path=args.vocals,
            instrumental_path=args.instrumental
        )
        print(f"\n✓ Success! Output saved to: {output_file}")
        return 0
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())