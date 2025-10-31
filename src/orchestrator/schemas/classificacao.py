from pydantic import BaseModel, EmailStr
from typing import Dict

class ClassificacaoIn(BaseModel):
    projeto: str
    email_relator: EmailStr | str = ""
    prioridade: str = ""

class ClassificacaoOut(BaseModel):
    tarefa_texto: str
    tarefa_campos: Dict[str, str]