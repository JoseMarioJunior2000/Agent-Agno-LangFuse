import os, re
from typing import Dict
from agno.workflow import Workflow
from orchestrator.clients.llm import make_agent
from orchestrator.core.logging import logger
from orchestrator.config.settings import Settings
from orchestrator.clients.http import make_session
from orchestrator.prompts.prompt import SUMMARY_AGENT_INSTRUCTION
from langfuse import observe, get_client   # <-- Langfuse

class SummaryWorkflow(Workflow):
    description: str = "Gera resumo estruturado a partir da conversa"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.resumo_agent = make_agent(
            name="Resumo Estruturado",
            api_key=settings.OPENAI_API_KEY,
            system_instructions=SUMMARY_AGENT_INSTRUCTION,
        )
        self.settings = settings

    @observe(name="SummaryWorkflow.executar", capture_input=True, capture_output=True)
    def executar(self, entrada: Dict):
        prompt = SUMMARY_AGENT_INSTRUCTION.format(
            nome=entrada.get("nome", ""),
            email=entrada.get("email", ""),
            telefone=entrada.get("telefone", "")
        ) + f"\n\nConversa:\n{entrada.get('conversa','')}"
        logger.info("Gerando resumo estruturado...")
        
        lf = get_client()
        model_id = getattr(getattr(self.resumo_agent, "model", None), "id", "unknown")
        with lf.start_as_current_generation(
            name="SummaryWorkflow.llm",
            model=model_id,
            input=prompt
        ) as gen:
            resumo_resp = (self.resumo_agent.run(prompt).content or "").strip()
            gen.update(output=resumo_resp)

        if not resumo_resp:
            logger.warning("Resumo vazio — não há contexto suficiente.")
            return {"texto_resumo": "", "campos": {}}

        campos = self._extrair_campos_resumo(resumo_resp)

        sess = make_session()
        resumo_webhook_url = self.settings.WEBHOOK_RESUMO_URL
        if resumo_webhook_url and (resumo_resp or any(v for v in campos.values())):
            try:
                sess.post(str(resumo_webhook_url), json={
                    "resumo_texto": resumo_resp,
                    "resumo_reduzido": campos
                }, timeout=6).raise_for_status()
            except Exception as e:
                logger.error(f"Falha ao enviar RESUMO para webhook: {e}")

        return {"texto_resumo": resumo_resp, "campos": campos}

    def _extrair_campos_resumo(self, texto: str):
        padroes = {
            "Nome": r"Nome:\s*(.*)",
            "Contatos": r"Contatos:\s*([^\n]*)\n\s*([^\n]*)",
            "Assunto Principal": r"Assunto Principal:\s*(.*)",
            "Descrição Breve": r"Descrição Breve:\s*(.*)",
            "Urgência": r"Urgência:\s*(.*)",
            "Ticket Type": r"Ticket Type:\s*(.*)"
        }
        resultado = {}
        for chave, padrao in padroes.items():
            m = re.search(padrao, texto, re.IGNORECASE)
            if m:
                if chave == "Contatos":
                    resultado[chave] = f"{m.group(1).strip()} / {m.group(2).strip()}"
                else:
                    resultado[chave] = m.group(1).strip()
            else:
                resultado[chave] = ""
        return resultado