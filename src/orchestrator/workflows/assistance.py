from typing import Dict
from agno.workflow import Workflow
from orchestrator.workflows.summary import SummaryWorkflow
from orchestrator.workflows.feedback import FeedbackWorkflow
from orchestrator.workflows.classifier import ClassifierWorkflow
from orchestrator.config.settings import Settings

class AssistanceWorkflow(Workflow):
    description: str = "Executa: Resumo -> Feedback -> Classificação de Tarefa"

    def __init__(self, settings: Settings):
        self.settings = settings

    def executar(self, entrada: Dict):
        resumo_wf = SummaryWorkflow(self.settings)
        r_out = resumo_wf.executar(entrada)
        texto_resumo = r_out.get("texto_resumo", "")
        campos_resumo = r_out.get("campos", {})

        if not texto_resumo:
            return {
                "resumo": r_out,
                "feedback": {"feedback_texto": "", "feedback_campos": {}},
                "tarefa": {"tarefa_texto": "", "tarefa_campos": {}}
            }

        assunto_principal = campos_resumo.get("Assunto Principal", "")
        descricao_breve = campos_resumo.get("Descrição Breve", "")

        feedback_wf = FeedbackWorkflow(self.settings)
        f_out = feedback_wf.executar({
            "texto_resumo": texto_resumo,
            "assunto_principal": assunto_principal,
            "descricao_breve": descricao_breve
        })

        problema = campos_resumo.get("Descrição Breve") or campos_resumo.get("Assunto Principal") or ""
        prioridade = campos_resumo.get("Urgência") or ""
        classificacao_wf = ClassifierWorkflow(self.settings)
        c_out = classificacao_wf.executar({
            "projeto": problema,
            "email_relator": entrada.get("email", ""),
            "prioridade": prioridade
        })

        return {"resumo": r_out, "feedback": f_out, "tarefa": c_out}
