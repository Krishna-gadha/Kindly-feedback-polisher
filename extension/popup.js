const API_URL = 'http://127.0.0.1:5000/convert';

let selectedTone = 'professional';
let selectedContext = 'email';

document.querySelectorAll('.pill:not(.ctx)').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.pill:not(.ctx)').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedTone = btn.dataset.tone;
    });
});

document.querySelectorAll('.pill.ctx').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.pill.ctx').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedContext = btn.dataset.context;
    });
});

document.getElementById('convert-btn').addEventListener('click', async () => {
    const text = document.getElementById('input-text').value.trim();
    if (!text) { showError('Please enter some text to convert.'); return; }

    showLoading(true);
    hideError();
    document.getElementById('output-section').classList.add('hidden');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, tone: selectedTone, context: selectedContext })
        });

        const data = await response.json();

        if (data.converted) {
            document.getElementById('output-text').textContent = data.converted;
            document.getElementById('score-line').textContent =
                `📊 ${data.input_politeness_label} (${data.input_politeness_score}%) → ${data.output_politeness_label} (${data.output_politeness_score}%)`;
            document.getElementById('output-section').classList.remove('hidden');

            if (data.message === 'Text is already polite. No conversion needed.') {
                showError('✅ Text is already polite. No conversion needed.');
            }
        } else {
            showError('Conversion failed. Please try again.');
        }
    } catch (err) {
        showError('Cannot connect to KINDLY server. Make sure app.py is running.');
    } finally {
        showLoading(false);
    }
});

document.getElementById('copy-btn').addEventListener('click', () => {
    const text = document.getElementById('output-text').textContent;
    navigator.clipboard.writeText(text).then(() => {
        document.getElementById('copy-btn').textContent = '✅ Copied!';
        setTimeout(() => { document.getElementById('copy-btn').textContent = '📋 Copy'; }, 2000);
    });
});

document.getElementById('clear-btn').addEventListener('click', () => {
    document.getElementById('input-text').value = '';
    document.getElementById('output-section').classList.add('hidden');
    hideError();
});

function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
    document.getElementById('convert-btn').disabled = show;
}

function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.classList.remove('hidden');
}

function hideError() {
    document.getElementById('error-msg').classList.add('hidden');
}

chrome.storage.local.get(['selectedText'], (result) => {
    if (result.selectedText) {
        document.getElementById('input-text').value = result.selectedText;
        chrome.storage.local.remove('selectedText');
    }
});