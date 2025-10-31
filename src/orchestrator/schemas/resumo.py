from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class ResumoIn(BaseModel):
    nome: Optional[str] = ""
    email: Optional[EmailStr] = None
    telefone: Optional[str] = ""
    conversa: str

class ResumoOut(BaseModel):
    texto_resumo: str
    campos: Dict[str, str]