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
    Pre-process Agent: Separates vocals from instrumental and extracts lyrics with timing
    Uses Spleeter for separation and Whisper for transcription
    """
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def separate_audio(self, song_path):
        """
        Separate vocals and instrumental using Spleeter
        Returns paths to separated files
        """
        print("[Pre-Process Agent] Separating vocals and instrumental...")
        
        try:
            from spleeter.separator import Separator
            
            # Use 2stems model (vocals and accompaniment)
            separator = Separator('spleeter:2stems')
            
            # Separate the audio
            song_name = Path(song_path).stem
            output_path = self.output_dir / "separated" / song_name
            
            separator.separate_to_file(song_path, str(self.output_dir / "separated"))
            
            vocals_path = output_path / "vocals.wav"
            instrumental_path = output_path / "accompaniment.wav"
            
            print(f"  ✓ Vocals saved to: {vocals_path}")
            print(f"  ✓ Instrumental saved to: {instrumental_path}")
            
            return str(vocals_path), str(instrumental_path)
            
        except Exception as e:
            print(f"  ✗ Error during separation: {e}")
            raise
    
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
    
    def process(self, song_path):
        """
        Main processing pipeline
        """
        print("\n" + "="*60)
        print("STAGE 1: PRE-PROCESSING")
        print("="*60)
        
        # Separate audio
        vocals_path, instrumental_path = self.separate_audio(song_path)
        
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
            print("  ⚠ Warning: No Gemini API key found. Set GEMINI_API_KEY environment variable.")
    
    def rewrite_lyrics(self, original_lyrics, theme):
        """
        Rewrite lyrics to match the given theme using Google Gemini
        """
        print("\n" + "="*60)
        print("STAGE 2: LYRIC GENERATION")
        print("="*60)
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
            
            # Validate response contains text
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
            return original_lyrics
    
    def process(self, lyrics_data, theme):
        """
        Main processing for lyric generation
        """
        return self.rewrite_lyrics(lyrics_data, theme)


class VoiceSynthAgent:
    """
    Voice Synthesis Agent: Placeholder for future voice synthesis implementation
    Would use TTS/voice cloning to generate new vocals
    """
    
    def __init__(self):
        pass
    
    def synthesize_voice(self, lyrics, reference_vocals_path):
        """
        Placeholder: Synthesize new vocals from lyrics
        In a full implementation, this would use TTS or voice cloning
        """
        print("\n" + "="*60)
        print("STAGE 3: VOICE SYNTHESIS")
        print("="*60)
        print("[Voice Synth Agent] Voice synthesis placeholder")
        print("  ⚠ This stage is not yet implemented")
        print("  → In the future, this would:")
        print("     - Analyze the reference vocal characteristics")
        print("     - Use TTS/voice cloning to generate new vocals")
        print("     - Match the prosody and style of the original")
        print("  → For now, returning original vocals path")
        
        return reference_vocals_path
    
    def process(self, lyrics_data, vocals_path):
        """
        Main processing for voice synthesis
        """
        return self.synthesize_voice(lyrics_data, vocals_path)


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
        print("\n" + "="*60)
        print("STAGE 4: ALIGNMENT")
        print("="*60)
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
        print("\n" + "="*60)
        print("STAGE 5: MIXING")
        print("="*60)
        print("[Mixer Agent] Mixing vocals and instrumental...")
        
        try:
            from pydub import AudioSegment
            
            # Load audio files
            print("  → Loading vocals...")
            vocals = AudioSegment.from_wav(vocals_path)
            
            print("  → Loading instrumental...")
            instrumental = AudioSegment.from_wav(instrumental_path)
            
            # Ensure both tracks are the same length
            # Trim or pad as needed
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
    
    def __init__(self, openai_api_key=None):
        self.preprocess_agent = PreProcessAgent()
        self.lyric_gen_agent = LyricGenerationAgent(api_key=openai_api_key)
        self.voice_synth_agent = VoiceSynthAgent()
        self.aligner_agent = AlignerAgent()
        self.mixer_agent = MixerAgent()
    
    def run(self, song_path, theme):
        """
        Run the full AI song transformation pipeline
        """
        print("\n" + "="*60)
        print("AI SONG PIPELINE")
        print("="*60)
        print(f"Input song: {song_path}")
        print(f"Theme: {theme}")
        print("="*60)
        
        try:
            # Stage 1: Pre-process (separation + transcription)
            preprocess_result = self.preprocess_agent.process(song_path)
            
            # Stage 2: Lyric Generation (rewrite to theme)
            new_lyrics = self.lyric_gen_agent.process(
                preprocess_result['lyrics_data'],
                theme
            )
            
            # Stage 3: Voice Synthesis (placeholder)
            synthesized_vocals = self.voice_synth_agent.process(
                new_lyrics,
                preprocess_result['vocals_path']
            )
            
            # Stage 4: Alignment (placeholder)
            aligned_vocals = self.aligner_agent.process(
                synthesized_vocals,
                preprocess_result['lyrics_data']
            )
            
            # Stage 5: Mixing (overlay vocals on instrumental)
            song_name = Path(song_path).stem
            output_name = f"{song_name}_themed_{theme.replace(' ', '_')}"
            final_output = self.mixer_agent.process(
                aligned_vocals,
                preprocess_result['instrumental_path'],
                output_name
            )
            
            print("\n" + "="*60)
            print("PIPELINE COMPLETE!")
            print("="*60)
            print(f"✓ Final output: {final_output}")
            print("="*60 + "\n")
            
            return final_output
            
        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
            raise


def main():
    """
    Main entry point with argument parsing
    """
    parser = argparse.ArgumentParser(
        description="AI Song Pipeline - Transform songs with AI-generated themed lyrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --song input.mp3 --theme "space exploration"
  python pipeline.py --song my_song.wav --theme "medieval fantasy"

Environment Variables:
  GEMINI_API_KEY - Google Gemini API key for lyric generation (required for full functionality)
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
        '--api-key',
        type=str,
        default=None,
        help='Google Gemini API key (alternatively set GEMINI_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    # Validate song file exists
    if not os.path.exists(args.song):
        print(f"Error: Song file not found: {args.song}")
        sys.exit(1)
    
    # Create and run pipeline
    pipeline = SongPipeline(openai_api_key=args.api_key)
    
    try:
        output_file = pipeline.run(args.song, args.theme)
        print(f"\n✓ Success! Output saved to: {output_file}")
        return 0
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
