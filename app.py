import os
from flask import Flask, request, jsonify, send_file
from model import AIProcessor

# Set up environment flags
# TOKENIZERS_PARALLELISM=False suppresses tokenizer warnings
# HF_HUB_OFFLINE ensures everything runs locally
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"  # critical for offline mode

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# Initialize the core AI processor (summarization, TTS, etc.)
ai_processor = AIProcessor()


@app.route('/api/tts-voices')
def get_voices():
    """Return the list of available voices from the local TTS engine."""
    voices = ai_processor.get_available_voices()
    return jsonify(voices)


@app.route('/api/tts', methods=['POST'])
def generate_speech():
    """Convert input text into speech using the selected voice and speed."""
    data = request.get_json()

    if not data or not data.get('text'):
        return jsonify({"error": "Missing text input"}), 400

    text = data['text']
    voice_id = data.get('voice_id')
    rate = data.get('rate', 175)  # default speech rate

    try:
        filepath = ai_processor.text_to_speech(text, voice_id, rate)
        if filepath:
            return send_file(filepath, as_attachment=True, mimetype='audio/aiff')
        return jsonify({"error": "Audio generation failed"}), 500

    except Exception as e:
        print("TTS error:", e)
        return jsonify({"error": "Something went wrong while generating audio"}), 500


@app.route('/api/process', methods=['POST'])
def process_text():
    """Summarize the provided text and extract any action items."""
    data = request.get_json()

    if not data or not data.get('text'):
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    summary = ai_processor.summarize(text)
    action_items = ai_processor.extract_action_items(text)

    return jsonify({
        "summary": summary,
        "action_items": action_items
    })


@app.route('/')
def index():
    """Serve the main frontend page."""
    return app.send_static_file('index.html')


if __name__ == '__main__':
    print("Starting QuickNote AI backend...")
    app.run(debug=True, port=5000)
