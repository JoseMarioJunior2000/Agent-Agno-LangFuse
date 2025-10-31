import re
from typing import Dict
from agno.workflow import Workflow
from orchestrator.clients.llm import make_agent
from orchestrator.core.logging import logger
from orchestrator.config.settings import Settings
from orchestrator.clients.http import make_session
from orchestrator.prompts.prompt import CLASSIFIER_AGENT_INSTRUCTION
from langfuse import observe  # <-- Langfuse
from src.orchestrator.core.trace import lf_client

class ClassifierWorkflow(Workflow):
    description: str = "Classifica tipo de tarefa, prioridade, data e agrega e-mail do relator"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.classificacao_agent = make_agent(
            name="Classificador de Tarefa",
            api_key=settings.OPENAI_API_KEY,
            system_instructions=CLASSIFIER_AGENT_INSTRUCTION,
        )
        self.settings = settings

    @observe(name="ClassifierWorkflow.executar", capture_input=True, capture_output=True)
    def executar(self, entrada: Dict):
        projeto = (entrada.get("projeto") or "").strip()
        email_relator = (entrada.get("email_relator") or "").strip()
        prioridade_in = (entrada.get("prioridade") or "").strip()

        if not projeto:
            logger.warning("Sem 'projeto' para classificação.")
            return {"tarefa_texto": "", "tarefa_campos": {}}

        prioridade_px = self._map_prioridade_deterministico(prioridade_in)

        prompt = self.classificacao_agent.instructions \
            .replace("{projeto}", projeto) \
            .replace("{email_relator}", email_relator or "N/A")
        prompt += f"\n\nPrioridade (original): {prioridade_in or 'N/D'}\n"

        logger.info("Classificando tarefa e prioridade...")

        lf = lf_client()
        model_id = getattr(getattr(self.classificacao_agent, "model", None), "id", "unknown")
        with lf.start_as_current_generation(
            name="ClassifierWorkflow.llm",
            model=model_id,
            input=prompt
        ) as gen:
            resp = (self.classificacao_agent.run(prompt).content or "").strip()
            gen.update(output=resp)
        
        campos = self._extrair_campos_classificacao(resp)

        if prioridade_px:
            campos["Prioridade"] = prioridade_px

        sess = make_session()
        tarefa_webhook_url = self.settings.WEBHOOK_CATEGORIA_URL
        if tarefa_webhook_url and (resp or any(v for v in campos.values())):
            try:
                sess.post(str(tarefa_webhook_url), json={
                    "tarefa_texto": resp,
                    "tarefa_campos": campos
                }, timeout=6).raise_for_status()
            except Exception as e:
                logger.error(f"Falha ao enviar TAREFA para webhook: {e}")

        return {"tarefa_texto": resp, "tarefa_campos": campos}

    def _map_prioridade_deterministico(self, prioridade_in: str) -> str:
        s = (prioridade_in or "").lower()
        if "🔴" in s or "crítica" in s or "critica" in s: return "P1"
        if "🟠" in s or "alta" in s:                          return "P2"
        if "🟡" in s or "média" in s or "media" in s:         return "P3"
        if "🟢" in s or "baixa" in s:                         return "P4"
        return ""

    def _extrair_campos_classificacao(self, texto: str):
        padroes = {
            "Projeto": r"Projeto:\s*(.+)",
            "Tarefa": r"Tarefa:\s*(.*)",
            "Prioridade": r"Prioridade:\s*(P[1-4])",
            "EmailRelator": r"EmailRelator:\s*([^\s]+@[^\s]+)"
        }
        out = {}
        for k, p in padroes.items():
            m = re.search(p, texto, flags=re.IGNORECASE)
            out[k] = m.group(1).strip() if m else ""

        tarefa_map = {
            "melhoria": "Melhoria",
            "melhorias": "Melhoria",
            "bug": "Bug",
            "nova funcionalidade": "Nova Funcionalidade",
            "novas funcionalidades": "Nova Funcionalidade",
        }
        t = out.get("Tarefa", "").lower()
        out["Tarefa"] = tarefa_map.get(t, out.get("Tarefa", "").strip())
        out["Projeto"] = re.sub(r"\s+", " ", out.get("Projeto", "")).strip()
        return out
