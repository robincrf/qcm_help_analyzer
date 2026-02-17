# QCM Screen Analyzer

Python application to automatically capture multiple-choice questions from the screen, extract text using OCR, and get answers via AI.

## ✨ Features

- **Automatic screenshot capture**: Press `=` to capture
- **Online OCR**: Text extraction via OCRSpace API (free)
- **AI analysis**: MCQ answers via Groq API (free)
- **Results popup**: Answers displayed in a popup window
- **No storage**: No data written to disk

## Prerequisites

- **Python 3.11+** (tested on Python 3.14)
- **macOS** (or Windows/Linux with adaptations)
- Free account: https://ocr.space/ocrapi
- Free account: https://console.groq.com

---

## Installation

### 1. Clone the project

```bash
git clone https://github.com/robincrf/qcm_easy.git
cd qcm_easy
cd tests
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
cd ../
pip install -r requirements.txt
```

---

## Configuration

### 1. Create the `.env` file

```bash
cp .env.example .env
```

### 2. Configure `.env`

```bash
OCRSPACE_API_KEY=your_ocrspace_key_here
OCR_LANGUAGE=fre
USE_LLM=true
GROQ_API_KEY=your_groq_key_here
DEBUG_MODE=false
DEBUG_SAVE_SCREENSHOTS=false
```

---

## Usage

Run the application:

```bash
python main.py
```

### Shortcuts
- `=` → Capture and analyze screen  
- `ESC` → Quit application  

### Workflow
1. Press `=` to capture the full screen  
2. OCR extracts MCQ text  
3. AI analyzes and finds answers  
4. A popup displays the results  

---

## Project structure

```
qcm-screen-analyzer/
├── src/
│   ├── capture.py
│   ├── ocr_api.py
│   └── llm_client.py
├── tests/
├── main.py
├── requirements.txt
├── .env.example
├── .env (not committed)
├── .gitignore
└── README.md
```

---

## Security

- API keys stored in `.env` (ignored by Git)  
- No screenshot storage by default  
- No sensitive logs  
- Network timeouts configured  
- **Never share your `.env` file**

---

## Free limits

| Service | Free limit |
|---|---|
| OCRSpace | 25,000 requests/month |
| Groq | 30 requests/min — 14,400/day |

---

## Contribution

Contributions are welcome via Issues and PRs.
