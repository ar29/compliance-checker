from pydantic import BaseModel
from typing import List, Any, Dict

class Issue(BaseModel):
    message: str
    context: str
    ruleId: str | None = None
    replacements: List[str] | None = None

class AnalyzeResponse(BaseModel):
    filename: str
    report: Dict[str, Any]
