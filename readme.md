QUICK_NOTE_AI

QuickNote AI is a full-stack web application designed to be a complete, offline-first productivity tool. It allows users to paste unstructured text, such as meeting transcripts or rough drafts, and instantly receive a concise summary and a neatly formatted list of action items. The entire AI process runs 100% locally, with no external API calls, ensuring user data remains private and the tool is functional without an internet connection.

Core Features

AI-Powered Summarization: Uses a local distilbart model from Hugging Face to generate clear and concise summaries.

Intelligent Action Item Extraction: A robust, rule-based engine parses conversational text to find and clean up tasks, filtering out non-actionable sentences.

100% Offline: The AI model and all backend logic run entirely on the local machine. We use HF_HUB_OFFLINE=1 to ensure no network requests are made.

Offline Text-to-Speech (TTS): Listen to any generated summary using the native TTS engine of your operating system.

Advanced Controls: Select from any voice installed on your system (including custom-installed voices like "Rishi" or "Veena").

Voice Search: A search bar to quickly filter the list of available voices.

Speed Slider: Adjust the playback speed from slow to fast.

Modern UI: A clean, responsive, and user-friendly interface built with vanilla HTML, CSS, and JavaScript.

Technology Stack

Backend: Python, Flask

AI/ML: Hugging Face transformers (using sshleifer/distilbart-cnn-6-6)

Text-to-Speech: pyttsx3 (to fetch available voice lists), Native macOS say command (for robust audio generation)

Frontend: HTML5, CSS3, Vanilla JavaScript

Setup and Installation

Follow these instructions to set up and run the project on your local machine.

1. Prerequisites

1.a)Python 3.8+

1.b)pip (Python package installer)

1.c)On Linux: You must install espeak: sudo apt-get install espeak

1.d)On macOS: The app uses the say command, which is pre-installed. pyobjc is included in requirements.txt.

2. Clone the Repository

#Replace this with your actual repository URL git clone https://github.com/your-username/quicknote-ai.git cd quicknote-ai

3. Set Up the Backend

All backend setup is done from the backend/ directory.

a) Navigate into the backend folder cd backend

b) Create a Python virtual environment python3 -m venv venv

c) Activate the virtual environment

On macOS/Linux: source venv/bin/activate

On Windows: venv\Scripts\activate

d) Install all required dependencies pip install -r requirements.txt

4. Download the AI Model (First-Time Only)

The very first time you run the app, you need to be online so it can download and cache the 400MB AI model.

a) Temporarily edit backend/app.py:

Comment out line 2: # os.environ["HF_HUB_OFFLINE"] = "1"

b) Temporarily edit backend/model.py:

In the init method, find the AutoTokenizer.from_pretrained and AutoModelForSeq2SeqLM.from_pretrained calls.

Remove the local_files_only=True parameter from both of them.

c) Run the app:

python3 app.py

Wait for the model to download (it will take a few minutes). Once the server is running (you'll see Running on http://127.0.0.1:5000), stop it with Ctrl+C.

d) Undo your changes:

Un-comment the line in app.py.

Re-add the local_files_only=True parameter in model.py.

The model is now cached, and the app will run 100% offline.

e) Running the Application

Make sure you are in the backend/ directory and your virtual environment is active. f) Run the Flask server:

python3 app.py

You will see an output similar to this, confirming the app is offline and running:

Loading summarization model...

*** SUCCESSFULLY LOADED MODEL IN OFFLINE MODE. ***

Model loaded successfully in 1.07 seconds.

Running on http://127.0.0.1:5000
Open your web browser and navigate to http://127.0.0.1:5000.

Project Structure

quicknote-ai/
│
├── backend/
│   ├── app.py             # Flask server, API routes
│   ├── model.py            # AI model loading, summarization, action items, TTS logic
│   ├── requirements.txt   # Python dependencies
│   └── audio_cache/       # Temporary folder for generated audio files
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── README.md              # This file

AI Assistance

I used an AI tool (Gemini) to help solve a specific debugging problem. The transformers library was still attempting to connect to the internet, despite the model being cached. The AI helped confirm the correct environment variable (HF_HUB_OFFLINE=1) and parameter (local_files_only=True) I needed to implement to get the app running in a true 100% offline mode.