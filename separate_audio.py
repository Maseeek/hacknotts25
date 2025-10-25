from flask import Flask, request, jsonify
from pathlib import Path
from spleeter.separator import Separator
import tempfile
import os

app = Flask(__name__)

@app.route('/split', methods=['POST'])
def split_audio():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        tmp_dir = tempfile.mkdtemp()
        song_path = os.path.join(tmp_dir, file.filename)
        file.save(song_path)

        output_dir = Path("output/separated")
        output_dir.mkdir(parents=True, exist_ok=True)

        separator = Separator('spleeter:2stems')
        separator.separate_to_file(song_path, str(output_dir))

        song_name = Path(file.filename).stem
        vocals_path = str(output_dir / song_name / "vocals.wav")
        instrumental_path = str(output_dir / song_name / "accompaniment.wav")

        return jsonify({
            "vocals_path": vocals_path,
            "instrumental_path": instrumental_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)
