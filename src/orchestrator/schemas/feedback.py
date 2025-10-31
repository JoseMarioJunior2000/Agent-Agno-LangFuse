from pydantic import BaseModel
from typing import Dict

class FeedbackIn(BaseModel):
    texto_resumo: str
    assunto_principal: str = ""
    descricao_breve: str = ""
    preferencia_contexto: str = ""

class FeedbackOut(BaseModel):
    feedback_texto: str
    feedback_campos: Dict[str, str]