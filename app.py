from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import T5ForConditionalGeneration, T5Tokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch
import re
import random

app = Flask(__name__)
CORS(app)

print("Loading model...")
model_path = "./model"
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)
device = torch.device("cpu")
model = model.to(device)
model.eval()

analyzer = SentimentIntensityAnalyzer()
print("Model loaded successfully")


def get_politeness_score(text):
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:
        return 100, "Already Polite"
    elif compound >= -0.05:
        return 60, "Neutral"
    elif compound >= -0.3:
        return 40, "Slightly Harsh"
    elif compound >= -0.6:
        return 20, "Harsh"
    else:
        return 5, "Very Harsh"


def clean_harsh_words(text):
    replacements = {
        "what the hell": "what on earth",
        "the hell": "on earth",
        "hell of a": "quite a",
        "hell": "heck",
        "stupidest": "least effective",
        "stupidity": "lack of clarity",
        "stupid": "unclear",
        "idiot": "person",
        "idiotic": "misguided",
        "dumb": "unclear",
        "dumbest": "least effective",
        "brainless": "uninformed",
        "utterly useless": "needs significant improvement",
        "completely useless": "needs significant improvement",
        "worthless": "needs more work",
        "useless": "needs improvement",
        "pathetic": "below expectations",
        "disgusting": "concerning",
        "ridiculous": "questionable",
        "absurd": "unexpected",
        "nonsense": "unclear",
        "rubbish": "needs revision",
        "garbage": "needs revision",
        "trash": "needs revision",
        "junk": "needs revision",
        "absolute mess": "needs restructuring",
        "complete mess": "needs restructuring",
        "total mess": "needs restructuring",
        "mess": "needs restructuring",
        "terrible": "needs improvement",
        "horrible": "needs attention",
        "awful": "needs work",
        "atrocious": "needs significant attention",
        "dreadful": "needs improvement",
        "appalling": "concerning",
        "abysmal": "below expectations",
        "damn": "quite",
        "damned": "quite",
        "crap": "not ideal",
        "crappy": "below standard",
        "sucks": "needs improvement",
        "suck": "needs improvement",
        "will crash": "may encounter issues",
        "crash": "fail gracefully",
        "errors": "issues",
        "completely broken": "needs significant fixing",
        "broken": "needs fixing",
        "you are the most": "this approach is among the most",
        "you are so": "this is quite",
        "you are a": "this seems",
        "you are": "this approach is",
        "your work is": "the work here is",
        "who even": "it is worth considering who",
        "waste of time": "not the most efficient use of time",
        "waste": "inefficient use",
        "get fired": "face performance consequences",
        "fire you": "address performance concerns",
        "fired": "let go",
    }
    lower = text.lower()
    for harsh, polite in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        lower = lower.replace(harsh, polite)
    return lower


def convert_text(harsh_text):
    input_text = "make polite: " + harsh_text
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=128,
        truncation=True
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=128,
            num_beams=4,
            early_stopping=True
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def apply_tone(base_output, tone, original_text):
    base = base_output.strip()
    base_clean = base.rstrip('.')

    if tone == "professional":
        prefixes = [
            "Upon review, ",
            "From a professional standpoint, ",
            "It is recommended that ",
            "For improved outcomes, ",
        ]
        prefix = random.choice(prefixes)
        return f"{prefix}{base_clean[0].lower()}{base_clean[1:]}."

    elif tone == "friendly":
        prefixes = [
            "Hey, just a thought — ",
            "No worries, but ",
            "Quick suggestion — ",
            "Just wanted to mention — ",
        ]
        prefix = random.choice(prefixes)
        return f"{prefix}{base_clean[0].lower()}{base_clean[1:]}! 😊"

    elif tone == "encouraging":
        suffixes = [
            " You're making great progress!",
            " Keep pushing forward!",
            " I know you can improve this!",
            " Small changes here will make a big difference!",
        ]
        suffix = random.choice(suffixes)
        return f"{base_clean}.{suffix}"

    elif tone == "empathetic":
        prefixes = [
            "I understand this is challenging — ",
            "I appreciate your effort here — ",
            "I can see you've been working hard — ",
            "I know this isn't easy — ",
        ]
        prefix = random.choice(prefixes)
        return f"{prefix}{base_clean[0].lower()}{base_clean[1:]}."

    elif tone == "humorous":
        templates = [
            f"{base_clean} — no pressure, but your code might be staging a rebellion! 😄",
            f"Plot twist: {base_clean[0].lower()}{base_clean[1:]}! Your future self will thank you. 😂",
            f"{base_clean}. Think of it as a glow-up for your code! ✨😄",
            f"Good news and better news — {base_clean[0].lower()}{base_clean[1:]}! 🎉",
        ]
        return random.choice(templates)

    else:
        return base


def apply_context(text, context):
    """
    Wraps the tone-adjusted text in a context-appropriate format.
    Context shapes the structure; tone shapes the voice.
    """
    text = text.strip()

    if context == "email":
        return (
            f"Subject: Feedback for Your Attention\n\n"
            f"Hi,\n\n"
            f"{text}\n\n"
            f"Please feel free to reach out if you have any questions.\n\n"
            f"Best regards"
        )

    elif context == "chat":
        # Short, no formality, fits a chat bubble
        # Strip any formal openers if present
        chat_text = text
        formal_openers = [
            "Upon review, ", "From a professional standpoint, ",
            "It is recommended that ", "For improved outcomes, ",
            "I understand this is challenging — ", "I appreciate your effort here — ",
            "I can see you've been working hard — ", "I know this isn't easy — ",
        ]
        for opener in formal_openers:
            if chat_text.startswith(opener):
                chat_text = chat_text[len(opener):]
                chat_text = chat_text[0].upper() + chat_text[1:]
                break
        return f"{chat_text} 👍"

    elif context == "review":
        return (
            f"Performance Feedback:\n\n"
            f"{text}\n\n"
            f"This feedback is intended to support continued growth and development."
        )

    elif context == "document":
        # Strip emojis and casual markers for formal document tone
        clean = re.sub(r'[^\x00-\x7F😊😄😂✨🎉👍]', '', text)
        clean = re.sub(r'[😊😄😂✨🎉👍]', '', clean).strip()
        # Remove casual openers
        casual_openers = ["Hey, just a thought — ", "No worries, but ", "Quick suggestion — ", "Just wanted to mention — "]
        for opener in casual_openers:
            if clean.startswith(opener):
                clean = clean[len(opener):]
                clean = clean[0].upper() + clean[1:]
                break
        return (
            f"Formal Note:\n\n"
            f"{clean}\n\n"
            f"This matter warrants careful consideration and timely action."
        )

    else:
        return text


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    harsh_text = data.get('text', '').strip()
    tone = data.get('tone', 'professional').lower()
    context = data.get('context', 'email').lower()

    if not harsh_text:
        return jsonify({'error': 'Empty text'}), 400

    input_score, input_label = get_politeness_score(harsh_text)

    if input_score >= 100:
        return jsonify({
            'original': harsh_text,
            'converted': harsh_text,
            'tone': tone,
            'context': context,
            'input_politeness_score': input_score,
            'input_politeness_label': input_label,
            'output_politeness_score': input_score,
            'output_politeness_label': input_label,
            'message': 'Text is already polite. No conversion needed.'
        })

    # Stage 2 — T5 base conversion + cleaning
    base_result = convert_text(harsh_text)
    base_result = clean_harsh_words(base_result)

    # Stage 3 — Tone application
    tone_result = apply_tone(base_result, tone, harsh_text)

    # Stage 4 — Context wrapping
    final_result = apply_context(tone_result, context)

    output_score, output_label = get_politeness_score(final_result)

    return jsonify({
        'original': harsh_text,
        'converted': final_result,
        'tone': tone,
        'context': context,
        'input_politeness_score': input_score,
        'input_politeness_label': input_label,
        'output_politeness_score': output_score,
        'output_politeness_label': output_label,
        'message': 'Conversion successful'
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'running'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)