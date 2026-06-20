from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import traceback
from youtube_transcript_api import YouTubeTranscriptApi
import together
import subprocess
import json
import os
from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException

app = Flask(__name__)
CORS(app)

# 1. FIXED KEYS AND ENDPOINTS
TOGETHER_API_KEY = "Your_API_Key_Here"
together.api_key = TOGETHER_API_KEY
TOGETHER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
TOGETHER_URL = "https://api.together.ai/v1/chat/completions"

chat_memory = {}

def call_llm_model(transcript):
    prompt = f"Summarize the following YouTube video transcript:\n\n{transcript}\n\nSummary:"
    
    # 2. FIXED PAYLOAD: Chat completions endpoint requires a "messages" list, not a flat "prompt"
    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
        "stop": ["User:", "Transcript:"]
    }

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(TOGETHER_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()

    # 3. FIXED PARSING: Extracting response based on standard OpenAI JSON output format
    return result['choices'][0]['message']['content'].strip()


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Welcome to the AI.dly Server Page!"})

def get_text_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

@app.route('/read_webpage', methods=['POST'])
def read_webpage():
    data = request.get_json() or {}
    url = data.get('url')
    session_id = 'default'

    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    try:
        text = get_text_from_url(url)
        if session_id not in chat_memory:
            chat_memory[session_id] = []

        chat_memory[session_id].append({
            "role": "system",
            "content": f"Webpage content from {url}:\n\n{text[:1000]}"
        })

        return jsonify({'text': text})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json() or {}
        text = data.get('text')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            return jsonify({'error': 'Missing text parameter'}), 400
            
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return jsonify({'translated_text': translated_text})
    except LanguageNotSupportedException:
        return jsonify({'error': f'Language code "{target_lang}" is not supported.'}), 400
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/essay', methods=['POST'])
def write_essay():
    data = request.get_json() or {}
    topic = data.get('topic', "").strip()
    if not topic:
        return jsonify({"error": "Topic is empty"}), 400
    
    try:
        prompt = f"Write a detailed essay on the topic: \"{topic}\".\n\nEssay:"

        # FIXED PAYLOAD STRUCTURE
        payload = {
            "model": TOGETHER_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
            "top_p": 0.9,
            "stop": ["User:", "Essay:"]
        }

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(TOGETHER_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # FIXED VALUE EXTRACTION
        essay_text = result['choices'][0]['message']['content'].strip()

        return jsonify({"essay": essay_text})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True) or {}
        session_id = 'default'
        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({"error": "Prompt is empty"}), 400

        if session_id not in chat_memory:
            chat_memory[session_id] = []

        # Safely convert historic data format to dict items if strings leak in
        sanitized_history = []
        for m in chat_memory[session_id]:
            if isinstance(m, dict):
                sanitized_history.append(m)
            elif isinstance(m, str):
                if ":" in m:
                    parts = m.split(":", 1)
                    sanitized_history.append({"role": parts[0].lower().strip(), "content": parts[1].strip()})
                else:
                    sanitized_history.append({"role": "user", "content": m})
        
        chat_memory[session_id] = sanitized_history

        # Add the new message block
        chat_memory[session_id].append({"role": "user", "content": prompt})

        # FIXED STRUCTURE: Send the actual chat array over directly, do not format down to a string
        payload = {
            "model": TOGETHER_MODEL,
            "messages": chat_memory[session_id],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 600,
            "stop": ["User:", "Assistant:"]
        }

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(TOGETHER_URL, headers=headers, json=payload)

        if response.status_code != 200:
            print("Together API Error:", response.text)
            return jsonify({"error": f"Together API call failed: {response.text}"}), 500

        result = response.json()
        # FIXED ARRAY KEY TARGETS
        ai_response = result['choices'][0]['message']['content'].strip()

        # Save assistant responses cleanly into system state histories as standard maps
        chat_memory[session_id].append({"role": "assistant", "content": ai_response})

        return jsonify({"response": ai_response})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500


@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files["file"]
    session_id = request.form.get("session_id", "default")

    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    if session_id not in chat_memory:
        chat_memory[session_id] = []

    chat_memory[session_id].append({
        "role": "system",
        "content": f"PDF content:\n\n{text[:1000]}"
    })

    return jsonify({"text": text[:4000]})

import subprocess

def get_subtitles_with_ytdlp(url):
    try:
        command = [
            'yt-dlp',
            '--write-sub',
            '--write-auto-sub',
            '--sub-lang', 'en',
            '--skip-download',
            '--sub-format', 'json3',
            '--print-json',
            url
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        print(" yt-dlp stdout:", result.stdout)
        print(" yt-dlp stderr:", result.stderr)

        metadata = json.loads(result.stdout.splitlines()[0])
        subtitles = metadata.get('requested_subtitles', {})
        sub_url = subtitles.get('en', {}).get('url')
        print(subtitles)

        if not sub_url:
            print(" No subtitles URL found")
            return None

        sub_result = subprocess.run(['curl', sub_url], capture_output=True, text=True)
        subtitle_json = json.loads(sub_result.stdout)

        transcript = []
        for event in subtitle_json['events']:
            if 'segs' in event:
                text = ''.join(seg['utf8'] for seg in event['segs'])
                transcript.append(text)

        return '\n'.join(transcript)

    except Exception as e:
        print("yt-dlp error:", e)
        return None


@app.route("/youtube_summary", methods=["POST"])
def summarize_youtube():
    try:
        data = request.get_json()
        url = data.get("url")

        transcript = get_subtitles_with_ytdlp(url)
        if not transcript:
            return jsonify({"error": "Transcript not found or blocked"}), 404

        summary = call_llm_model(transcript)
        return jsonify({"summary": summary})
    
    except Exception as e:
        print("Flask route error:", e)
        return jsonify({"error": str(e)}), 500





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
