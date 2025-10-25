from pathlib import Path
@app.route('/split', methods=['POST'])
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
            instrumental_path = output_path / "instrumental.wav"

            print(f"  ✓ Vocals saved to: {vocals_path}")
            print(f"  ✓ Instrumental saved to: {instrumental_path}")

            return str(vocals_path), str(instrumental_path)

        except Exception as e:
            print(f"  ✗ Error during separation: {e}")
            raise
if __name__ == '__main__':
    app.run(port=5001)