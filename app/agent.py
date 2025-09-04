import os
import language_tool_python
import spacy
from typing import List, Dict, Any
import openai

# Try to load a small English model; instruct users in README to install it.
try:
    nlp = spacy.load('en_core_web_sm')
except Exception:
    nlp = spacy.blank('en')

# initialize LanguageTool once
tool = language_tool_python.LanguageTool('en-US')

def analyze_text(text: str) -> Dict[str, Any]:
    """Run LanguageTool checks and spaCy-based rules, return report dict."""
    matches = tool.check(text)
    issues = []
    for m in matches:
        issues.append({
            'message': m.message,
            'context': m.context,
            'ruleId': getattr(m, 'ruleId', None),
            'replacements': m.replacements,
            'offsetInContext': getattr(m, 'offsetInContext', None)
        })

    # spaCy analysis: sentence length, passive voice, readability hint (Flesch via heuristic)
    doc = nlp(text)
    long_sentences = []
    passive_sentences = []
    for sent in doc.sents:
        tokens = [t for t in sent if not t.is_punct]
        if len(tokens) > 22:
            long_sentences.append({'text': sent.text, 'length': len(tokens)})
        # simple passive voice detection using dependency labels
        # look for 'auxpass' or 'nsubjpass' in token dependencies (works with en_core_web_sm)
        for token in sent:
            if token.dep_ in ('auxpass', 'nsubjpass'):
                passive_sentences.append({'text': sent.text})
                break

    # very simple readability estimator (average sentence length)
    sentences = list(doc.sents)
    avg_sent_len = sum(len([t for t in s if not t.is_punct]) for s in sentences) / max(1, len(sentences))
    readability = {'avg_sentence_length': avg_sent_len}

    return {'issues': issues, 'long_sentences': long_sentences, 'passive_sentences': passive_sentences, 'readability': readability}

# Prompt engineering: template and chunking strategy
PROMPT_TEMPLATE = ("You are a professional editor. Rewrite the following passage to improve grammar, clarity, and conciseness, preserving the original meaning. " 
                   "Guidelines: use formal tone; avoid passive voice; keep sentences under 22 words; prefer active verbs; do not introduce new facts. " 
                   "Return only the rewritten passage without commentary.\n\nOriginal passage:\n{chunk}\n\nRewritten passage:")

def _call_openai_for_chunk(chunk: str) -> str:
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        raise RuntimeError('OPENAI_API_KEY not set')
    messages = [
        {'role': 'system', 'content': 'You are a concise and careful editor.'},
        {'role': 'user', 'content': PROMPT_TEMPLATE.format(chunk=chunk)}
    ]
    resp = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages, temperature=0.2, max_tokens=1500)
    return resp.choices[0].message.content.strip()

def rewrite_text(text: str) -> str:
    """Rewrite text using OpenAI if available. Chunk to avoid token limits. Fall back to LanguageTool if no API key."""
    key = os.getenv('OPENAI_API_KEY', None)
    if not key:
        return tool.correct(text)

    # chunk by paragraphs (simple)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    rewritten_paras = []
    for para in paragraphs:
        # if too long, further split by sentence to keep chunk size reasonable
        if len(para) > 3000:
            sents = [s.text for s in nlp(para).sents]
            chunk = ''
            for s in sents:
                if len(chunk) + len(s) > 3000:
                    rewritten_paras.append(_call_openai_for_chunk(chunk))
                    chunk = s
                else:
                    chunk += ' ' + s
            if chunk.strip():
                rewritten_paras.append(_call_openai_for_chunk(chunk))
        else:
            rewritten_paras.append(_call_openai_for_chunk(para))
    return '\n\n'.join(rewritten_paras)
