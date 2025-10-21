# backend/test_tts.py
import pyttsx3
import os

try:
    print("Attempting to initialize pyttsx3 engine...")
    engine = pyttsx3.init()
    print("✅ Engine initialized successfully.")

    text = "If this audio file is created, the test is successful."
    filepath = "test_output.mp3"

    print(f"Attempting to save speech to '{filepath}'...")
    engine.save_to_file(text, filepath)
    engine.runAndWait()

    if os.path.exists(filepath):
        print(f"✅ Success! Audio file '{filepath}' was created.")
        os.remove(filepath) # Clean up the test file
    else:
        print(f"❌ Failure! The audio file was not created.")

except Exception as e:
    print(f"\n❌ An error occurred during the test: {e}")