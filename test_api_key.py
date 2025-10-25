#!/usr/bin/env python3
"""
Test script for VoiceSynthAgent
Tests voice analysis and synthesis with Gemini + ElevenLabs
Compatible with Python 3.12+
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import save

# Load environment variables
load_dotenv()


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
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("  ✓ Gemini initialized")
            except Exception as e:
                print(f"  ✗ Could not initialize Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        # Initialize ElevenLabs client if available
        if self.elevenlabs_api_key:
            try:   
                self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)
                print("  ✓ ElevenLabs initialized")
            except Exception as e:
                print(f"  ✗ Could not initialize ElevenLabs: {e}")
                self.elevenlabs_client = None
        else:
            self.elevenlabs_client = None

    def get_voice_description(self, artist_name):
        """
        Use Gemini to generate a detailed voice description based on artist name
        """
        if not self.gemini_model:
            return f"Voice similar to {artist_name}"
        
        print(f"\n[Step 1] Analyzing vocal characteristics of {artist_name}...")
        
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
            print(f"\n{description}\n")
            return description
        except Exception as e:
            print(f"  ✗ Error generating voice description: {e}")
            return f"Voice similar to {artist_name}, expressive and clear"

    def get_available_voices(self):
        """
        Get list of available ElevenLabs voices
        """
        if not self.elevenlabs_client:
            return []
        
        try:
            response = self.elevenlabs_client.voices.get_all()
            return response.voices
        except Exception as e:
            print(f"  ✗ Error fetching voices: {e}")
            return []

    def get_best_voice_match(self, voice_description, artist_name):
        """
        Use Gemini to intelligently select the best ElevenLabs voice based on description
        """
        if not self.gemini_model:
            return "pNInz6obpgDQGcFmaJgB"  # Default Adam voice ID
        
        print(f"[Step 2] Selecting best voice match for {artist_name}...")
        
        # Get available voices
        available_voices = self.get_available_voices()
        
        if not available_voices:
            print("  ⚠ No voices available, using default voice")
            return "pNInz6obpgDQGcFmaJgB"  # Adam voice ID
        
        print(f"  → Found {len(available_voices)} available voices")
        
        # Format voice list for Gemini
        voice_list = []
        for v in available_voices:
            voice_info = f"- {v.name} (ID: {v.voice_id})"
            if hasattr(v, 'labels') and v.labels:
                labels = ', '.join([f"{k}: {val}" for k, val in v.labels.items()])
                voice_info += f" - Labels: {labels}"
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
            
            # Find the voice_id for the selected voice name
            for v in available_voices:
                if v.name.lower() == voice_name.lower():
                    print(f"  ✓ Selected voice: {v.name} (ID: {v.voice_id})")
                    return v.voice_id
            
            # If not found, use first available
            print(f"  ⚠ Voice '{voice_name}' not found, using first available")
            print(f"  ✓ Using: {available_voices[0].name}")
            return available_voices[0].voice_id
                
        except Exception as e:
            print(f"  ✗ Error selecting voice: {e}")
            return "pNInz6obpgDQGcFmaJgB"  # Default Adam voice ID

    def synthesize_voice(self, lyrics, artist_name=None):
        """
        Synthesize new vocals from lyrics using AI-selected voice
        """
        print("\n" + "=" * 60)
        print("VOICE SYNTHESIS TEST")
        print("=" * 60)
        
        # Check if we have the necessary API keys
        if not self.elevenlabs_client:
            print("  ✗ Voice synthesis not available (no ElevenLabs API key)")
            return None
        
        # Get voice description from Gemini if artist name provided
        if artist_name:
            voice_description = self.get_voice_description(artist_name)
            selected_voice_id = self.get_best_voice_match(voice_description, artist_name)
        else:
            selected_voice_id = "pNInz6obpgDQGcFmaJgB"  # Default Adam voice
            print(f"[Voice Synth] Using default voice")
        
        # Generate vocals with AI-selected voice
        print(f"\n[Step 3] Generating vocals with voice ID: {selected_voice_id}...")
        
        try:
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                text=lyrics,
                voice_id=selected_voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            # Save the audio
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "test_vocals.mp3"
            
            # Convert generator to bytes and save
            audio_bytes = b"".join(audio_generator)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"  ✓ Vocals generated successfully")
            print(f"  ✓ Saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"  ✗ Error during voice synthesis: {e}")
            print(f"     Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None


def test_voice_synthesis():
    """
    Test the VoiceSynthAgent with sample lyrics
    """
    print("\n" + "=" * 60)
    print("TESTING VOICE SYNTHESIS AGENT")
    print("=" * 60)
    
    # Sample lyrics to test with
    test_lyrics = """
    We're floating through the cosmos, reaching for the stars,
    Past the moon and Jupiter, heading straight to Mars.
    The universe is calling, adventure in our veins,
    Space exploration dreams running through our brains.
    """
    
    # Test cases
    test_cases = [
        {
            "artist": "Drake",
            "description": "Testing with Drake's voice style"
        },
        {
            "artist": "J. Cole",
            "description": "Testing with J. Cole's voice style"
        },
        {
            "artist": "Kendrick Lamar",
            "description": "Testing with Kendrick Lamar's voice style"
        }
    ]
    
    # Initialize agent
    print("\nInitializing VoiceSynthAgent...")
    agent = VoiceSynthAgent()
    
    # Check if APIs are configured
    if not agent.gemini_api_key:
        print("\n⚠ Gemini API key not found!")
        print("Set GEMINI_API_KEY in your .env file or environment")
        return
    
    if not agent.elevenlabs_api_key:
        print("\n⚠ ElevenLabs API key not found!")
        print("Set ELEVENLABS_API_KEY in your .env file or environment")
        return
    
    print("\n✓ All APIs configured\n")
    
    # Run test for first artist
    print("=" * 60)
    print(f"TEST: {test_cases[0]['description']}")
    print("=" * 60)
    print(f"\nTest lyrics:\n{test_lyrics}\n")
    
    output_path = agent.synthesize_voice(
        lyrics=test_lyrics.strip(),
        artist_name=test_cases[0]['artist']
    )
    
    if output_path:
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
        print("=" * 60)
        print(f"✓ Audio file created: {output_path}")
        print("\nYou can play it with:")
        print(f"  afplay {output_path}  # macOS")
        print(f"  aplay {output_path}   # Linux")
        print(f"  start {output_path}   # Windows")
    else:
        print("\n✗ Test failed - no audio generated")
    
    print("\n" + "=" * 60 + "\n")


def quick_test(artist_name, lyrics=None):
    """
    Quick test function for specific artist
    """
    if lyrics is None:
        lyrics = "Testing one two three, this is a voice synthesis test."
    
    print(f"\nQuick test with {artist_name}")
    print(f"Lyrics: {lyrics}\n")
    
    agent = VoiceSynthAgent()
    output = agent.synthesize_voice(lyrics, artist_name)
    
    if output:
        print(f"\n✓ Success! Play with: afplay {output}")
    
    return output


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # Quick test mode
        artist = sys.argv[1]
        lyrics = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        quick_test(artist, lyrics)
    else:
        # Full test mode
        test_voice_synthesis()