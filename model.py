from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import pyttsx3
import subprocess
import re
import uuid
import time
import os
import shlex


class AIProcessor:
    def __init__(self):
        print("Loading summarization model...")
        start = time.time()

        # Load local DistilBART model for offline summarization
        model_name = "sshleifer/distilbart-cnn-6-6"

        tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name, local_files_only=True)
        self.summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

        print("Model loaded in offline mode successfully.")
        print(f"Model init time: {time.time() - start:.2f} sec")

        # Initialize TTS engine (for voice listing only)
        try:
            self.tts_engine = pyttsx3.init(driverName="nsss")
            print("TTS engine initialized.")
        except Exception as e:
            print(f"Warning: could not initialize TTS engine — {e}")
            self.tts_engine = None

        # Create cache directory for audio files
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_cache = os.path.join(self.base_dir, "audio_cache")
        os.makedirs(self.audio_cache, exist_ok=True)

    def get_available_voices(self):
        """Return list of voices available on the system."""
        if not self.tts_engine:
            return [{"id": "Alex", "name": "Alex", "lang": ["en_US"]}]
        
        voices = []
        for v in self.tts_engine.getProperty("voices"):
            voices.append({
                "id": v.name,
                "name": v.name,
                "lang": v.languages
            })
        return voices

    def text_to_speech(self, text, voice_id="Alex", rate=175):
        """Generate speech from text using macOS `say` command."""
        if not text.strip():
            return None

        filename = f"{uuid.uuid4()}.aiff"
        path = os.path.join(self.audio_cache, filename)

        try:
            # Use shell-safe quoting
            cmd = f"say -v {shlex.quote(voice_id)} -r {shlex.quote(str(rate))} -o {shlex.quote(path)} {shlex.quote(text)}"
            subprocess.run(cmd, shell=True, check=True)

            if os.path.exists(path):
                return path
            else:
                print(f"Error: audio file not found — {path}")
                return None

        except subprocess.CalledProcessError as e:
            print(f"Error during TTS: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during TTS: {e}")
            return None

    def summarize(self, text, min_length=50, max_length=200):
        """Summarize a given text."""
        if not text.strip():
            return ""
        result = self.summarizer(text, min_length=min_length, max_length=max_length, do_sample=False)
        return result[0]["summary_text"]

    def extract_action_items(self, text):
        """Extract actionable items from conversational text."""
        if not text.strip():
            return []

        # Clean up timestamps and speaker tags
        cleaned = re.sub(r'\[\d{2}:\d{2}:\d{2}\]\s*', '', text)
        cleaned = re.sub(r'\b\w+:\s', '', cleaned)

        patterns = [
            re.compile(r'(?i)\b(ACTION|TODO|ASSIGN|FOLLOW UP)[:\s]+([^.\n]+)'),
            re.compile(r'(?i)\b(?:we need|needs? to|is to|must)\s+(?:to\s)?([^.\n]+)'),
            re.compile(r'(?i)\b(?:I\'ll|I will)\s+(?:take|handle|work on|do)\s+([^.\n]+)'),
            re.compile(r'(?i)\b(?:we should|let\'s)\s+([^.\n]+)')
        ]

        items = []
        for p in patterns:
            for match in p.findall(cleaned):
                val = match[-1] if isinstance(match, tuple) else match
                items.append(val.strip())

        if not items:
            return []

        # Remove duplicates, filter short or unclear ones
        unique = list(dict.fromkeys(items))
        final = []
        for item in unique:
            if item.endswith('?'):
                continue
            for prefix in ['probably ', 'maybe ', 'just ', 'we need to ']:
                if item.lower().startswith(prefix):
                    item = item[len(prefix):]
            item = item.split('—')[0].split('because')[0].strip().capitalize()
            if len(item.split()) < 3:
                continue
            if not any(item != other and item in other for other in unique):
                final.append(item)
        return final
