from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import tempfile, os, uuid
from .processor import extract_text_from_file
from .agent import analyze_text, rewrite_text
from .generator import create_docx_from_text, create_pdf_from_text
from pathlib import Path
import zipfile

app = FastAPI(title='AI Document Compliance Checker')

@app.post('/analyze')
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail='Only .pdf and .docx are supported')
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        text = extract_text_from_file(tmp_path)
        report = analyze_text(text)
        return JSONResponse({'filename': file.filename, 'report': report})
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

@app.post('/correct')
async def correct(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail='Only .pdf and .docx are supported')
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    tmpdir = Path(tempfile.mkdtemp())
    try:
        text = extract_text_from_file(tmp_path)
        # Attempt GPT rewrite; fallback to LanguageTool-only if no API key
        rewritten = rewrite_text(text)
        docx_path = tmpdir / (Path(file.filename).stem + '_corrected.docx')
        pdf_path = tmpdir / (Path(file.filename).stem + '_corrected.pdf')
        create_docx_from_text(rewritten, str(docx_path))
        create_pdf_from_text(rewritten, str(pdf_path))
        # Zip both files
        zip_path = tmpdir / (Path(file.filename).stem + '_corrected.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.write(docx_path, docx_path.name)
            zf.write(pdf_path, pdf_path.name)
        return FileResponse(str(zip_path), media_type='application/zip', filename=zip_path.name)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
