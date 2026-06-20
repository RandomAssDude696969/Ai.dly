# AI.dly Server Backend

AI.dly is a modular, high-utility Flask backend server designed to process data from various sources (webpages, PDFs, YouTube transcripts) and augment them using advanced language models via Together AI, along with fully free language translation.

## Inspiration
I had made this project when the only such implementation was Sider.ai (I didn't know about GitHub at that time), and when I had to do a school research project, but ran out of commands on it. I had even used this in a Techfest, but had sadly missed out on the first prize by an inch.

## Features

* **AI Chat with Session Memory**: Multi-turn conversation processing using flagship serverless LLMs.
* **YouTube Transcript Summarization**: Extracts English audio scripts via yt-dlp tool sub-engines and builds brief topic reviews.
* **Document Text Extraction**: Reads uploaded PDF files dynamically using PyMuPDF (fitz).
* **Web Scraping Engine**: Cleans and extracts raw, script-free readable copy from public URLs.
* **Free Language Translation**: Auto-detects input dialects and converts text with zero API keys required.
* **Cross-Origin Enabled**: Integrated with flask-cors for effortless frontend connections.

---

## Tech Stack

* **Core Framework**: Python 3.12+, Flask
* **AI Engine**: Together AI (OpenAI-Compatible Chat Completions API)
* **Scraping & Parsers**: Beautiful Soup 4, PyMuPDF (fitz)
* **System Utilities**: yt-dlp, curl (system level dependency)
* **Utilities**: deep-translator, youtube-transcript-api

---

## Getting Started

## 0. Getting a Together.ai API key:
1) Create a free account at Together AI.
2) Navigate to the API Keys section in your dashboard.
3) Generate a new API key.
4) Copy the generated key and keep it secure.
5) Set the key as an environment variable before starting the server.

### 1. System Dependencies
This project utilizes the command-line utility `yt-dlp` and system `curl` to extract streaming subtitles. Ensure they are installed on your host machine environment:
```bash
# Ubuntu/Debian Linux
sudo apt update && sudo apt install yt-dlp curl

# macOS
brew install yt-dlp curl
```

### 2. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/RandomAssDude696969/Ai.dly/main
cd Ai.dly/ai.dly
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install flask flask-cors requests pymupdf beautifulsoup4 youtube-transcript-api deep-translator together
```

### 4. Set Up Environment Variables
Create an environment variable for your Together AI authentication key:
```bash
export TOGETHER_API_KEY="your_actual_together_api_token_here"
# On Windows Command Prompt: set TOGETHER_API_KEY="your_actual_together_api_token_here"
# On Windows PowerShell: \$env:TOGETHER_API_KEY="your_actual_together_api_token_here"
```

### 5. Run the Server
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

### 6. YouTube Transcript Summarizer
* **Route**: POST /youtube_summary
* **Payload**:
  ```json
  { "url": "https://youtube.com" }
  ```
## System Architecture

```text
┌─────────────────────────────────────────────┐
│               Chrome Extension              │
├─────────────────────────────────────────────┤
│ Chat UI                                     │
│ Essay Generator                             │
│ PDF Upload Interface                        │
│ Webpage Summarizer                          │
│ Translation Interface                       │
└───────────────────┬─────────────────────────┘
                    │ REST API (JSON)
                    ▼
┌─────────────────────────────────────────────┐
│                Flask Backend                │
├─────────────────────────────────────────────┤
│ Routing Layer                               │
│ Session Memory Management                   │
│ Request Validation                          │
│ Response Formatting                         │
└───────┬──────────┬──────────┬──────────┬────┘
        │          │          │          │
        ▼          ▼          ▼          ▼

┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ TogetherAI │ │ PyMuPDF  │ │ BS4      │ │ DeepTranslator│
│ LLM Engine │ │ PDF Parse│ │ Web Parse│ │ Translation   │
└─────┬──────┘ └──────────┘ └──────────┘ └──────────────┘
      │
      ▼
┌─────────────────────────────────────────────┐
│ Chat Generation                             │
│ Essay Generation                            │
│ Summarization                               │
│ Context-Aware Responses                     │
└─────────────────────────────────────────────┘

                    ▲
                    │
          ┌─────────┴─────────┐
          │ Transcript Layer  │
          ├───────────────────┤
          │ yt-dlp            │
          │ youtube-transcript│
          └───────────────────┘
```

## Request Flow Example

```text
User Prompt
    │
    ▼
Chrome Extension
    │
POST /chat
    │
    ▼
Flask Backend
    │
Session Context Injection
    │
    ▼
Together AI API
    │
LLM Response
    │
    ▼
JSON Response
    │
    ▼
Extension UI Render
```
