# KINDLY — AI-Powered Feedback Polisher

KINDLY automatically transforms harsh, aggressive text into polite, 
professional communication using a fine-tuned T5-small transformer model.

## Features
- 5 tone modes: Professional, Friendly, Encouraging, Empathetic, Humorous
- 4 context modes: Email, Chat, Performance Review, Formal Document
- Chrome Extension with Cmd+Shift+K shortcut
- Zero data storage — everything runs locally
- ROUGE-L: 0.6373 | BLEU-4: 0.5396

## Tech Stack
- Python, Flask, PyTorch
- T5-small (HuggingFace Transformers)
- VADER Sentiment Analysis
- Chrome Extension (Manifest V3)
- HTML, CSS, JavaScript

## How to Run
1. Install requirements:
pip install flask flask-cors transformers torch vaderSentiment sentencepiece

2. Start the API:
python3 app.py

3. Open the website:
open -a "Google Chrome" index.html

4. Load Chrome Extension:
Go to chrome://extensions → Load unpacked → select the extension folder

## Three Stage Pipeline
- Stage 1: VADER sentiment gate — checks if text is already polite
- Stage 2: T5 model converts harsh text + clean_harsh_words removes residual harshness
- Stage 3: apply_tone adds tone specific phrasing + apply_context formats for register

## Training
- Phase 1: 1,500 technical pairs (code reviews, security feedback)
- Phase 2: 185 general pairs (workplace, academic, interpersonal)
- Phase 3: 400 Civil Comments pairs (self-labeling technique)
- Final ROUGE-L: 0.6373 | BLEU-4: 0.5396

## Team
- Nandana Sankar (241160072)
- Pavitra Ashwin (241160061)
- Krishnagadha SP (241160017)

B.Tech CSE AI & ML — Chinmaya Vishwa Vidyapeeth, March 2026# Kindly-feedback-polisher
