from pydantic import BaseModel, EmailStr
from typing import Dict

class AtendimentoIn(BaseModel):
    nome: str = ""
    email: EmailStr | str = ""
    telefone: str = ""
    conversa: str

class AtendimentoOut(BaseModel):
    resumo: Dict
    feedback: Dict
    tarefa: Dict