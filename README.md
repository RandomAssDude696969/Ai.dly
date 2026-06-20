# AI.dly Server Backend

AI.dly is a modular, high-utility Flask backend server designed to process data from various sources (webpages, PDFs, YouTube transcripts) and augment them using advanced language models via Together AI, along with fully free language translation.

## Features

* **AI Chat with Session Memory**: Multi-turn conversation processing using flagship serverless LLMs.
* **YouTube Transcript Summarization**: Auto-fetches English video transcripts and provides concise overviews.
* **Document Text Extraction**: Reads uploaded PDF files dynamically using PyMuPDF (fitz).
* **Web Scraping Engine**: Cleans and extracts raw, script-free readable copy from public URLs.
* **Free Language Translation**: Auto-detects input dialects and converts text with zero API keys required.
* **Cross-Origin Enabled**: Integrated with flask-cors for effortless frontend connections.

---

## Tech Stack

* **Core Framework**: Python 3.12+, Flask
* **AI Engine**: Together AI (OpenAI-Compatible Chat Completions API)
* **Scraping & Parsers**: Beautiful Soup 4, PyMuPDF (fitz)
* **Utilities**: deep-translator, youtube-transcript-api

---

## Getting Started

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com
cd aidly-backend
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install flask flask-cors requests pymupdf beautifulsoup4 youtube-transcript-api deep-translator together
```

### 3. Set Up Environment Variables
Create an environment variable for your Together AI authentication key:
```bash
export TOGETHER_API_KEY="your_actual_together_api_token_here"
# On Windows Command Prompt: set TOGETHER_API_KEY="your_actual_together_api_token_here"
# On Windows PowerShell: \$env:TOGETHER_API_KEY="your_actual_together_api_token_here"
```

### 4. Run the Server
```bash
python app.py
```
The server will boot locally at http://127.0.0.

---

## API Endpoints Reference

### 1. AI Chat Endpoint
* **Route**: POST /chat
* **Payload**:
  ```json
  { "prompt": "Explain Quantum Computing like I am five years old." }
  ```

### 2. Multi-Language Translator
* **Route**: POST /translate
* **Payload**:
  ```json
  { "text": "Bonjour tout le monde", "target_lang": "en" }
  ```

### 3. Webpage Reader
* **Route**: POST /read_webpage
* **Payload**:
  ```json
  { "url": "https://example.com" }
  ```

### 4. Document PDF Reader
* **Route**: POST /read_pdf
* **Type**: multipart/form-data
* **Body**: file (Binary PDF File), session_id (Optional String)

### 5. Automated Essay Writer
* **Route**: POST /essay
* **Payload**:
  ```json
  { "topic": "Impact of Renewable Energy in 2026" }
  ```
