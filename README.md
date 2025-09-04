# AI Document Compliance Checker (FastAPI)

**Overview**
This project is a FastAPI-based API that accepts PDF/DOCX uploads, analyzes them against English writing guidelines using LanguageTool and OpenAI GPT, and can produce corrected `.docx` and `.pdf` outputs.

## Status
![CI](https://github.com/your-username/compliance_checker/workflows/CI/badge.svg)

**Important:** For security, **do not** put your OpenAI API key directly into the source. Use the environment variable `OPENAI_API_KEY` or a `.env` file (see `.env.example`). This repo intentionally does NOT include any API keys.

## Quickstart (local)

1. Create and activate a Python virtual environment (Python 3.9+ recommended).
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
2. Create `.env` or export the OpenAI key:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```
or create `.env` from `.env.example` and edit it.

3. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. API docs are available at `http://127.0.0.1:8000/docs`.

## Endpoints
- `POST /analyze` — Accept `file` (multipart/form-data). Returns JSON compliance report.
- `POST /correct` — Accept `file` (multipart/form-data). Returns a ZIP containing corrected `.docx` and `.pdf`.

## Development & Tests (GitHub Actions)
This project includes a CI workflow that runs `pytest`. The workflow is defined in `.github/workflows/ci.yml`.

Run tests locally:
```bash
pytest -q
```

## Prompt engineering tips
The repo includes an example prompt template used to ask GPT to rewrite documents. Key tips:
- Provide the model with an explicit role and desired output format.
- Limit rewrite scope (e.g. paragraph-by-paragraph) to avoid token limits.
- Ask for conservative edits (preserve meaning) and list the specific guidelines (formal tone, no passive voice, concise sentences under 22 words, etc.).

Example prompt (see `app/agent.py` for template):
> You are a professional editor. Rewrite the following text to improve grammar, clarity, and conciseness, preserving meaning. Use formal tone, avoid passive voice, and keep sentences shorter than 22 words. Output only the rewritten text.

## Contributing
See `CONTRIBUTING.md` for guidelines on running tests and submitting PRs.

## License
MIT
