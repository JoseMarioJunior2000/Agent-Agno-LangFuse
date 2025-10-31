import re, os
from typing import Dict
from agno.workflow import Workflow
from orchestrator.clients.llm import make_agent
from orchestrator.core.logging import logger
from orchestrator.config.settings import Settings
from orchestrator.clients.http import make_session
from orchestrator.prompts.prompt import FEEDBACK_AGENT_INSTRUCTION
from langfuse import observe, get_client  # <-- Langfuse

class FeedbackWorkflow(Workflow):
    description: str = "Gera feedback a partir do resumo, herdando título/comentário e determinando contexto"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.contexto_agent = make_agent(
            name="Classificador de Contexto",
            api_key=settings.OPENAI_API_KEY,
            system_instructions=FEEDBACK_AGENT_INSTRUCTION,
        )
        self.settings = settings

    def _extrair_contexto_com_llm(self, texto_resumo: str) -> str:
        resp = (self.contexto_agent.run(
            self.contexto_agent.instructions + "\n\nRESUMO ESTRUTURADO:\n" + (texto_resumo or "")
        ).content or "").strip()

        full_prompt = self.contexto_agent.instructions + "\n\nRESUMO ESTRUTURADO:\n" + (texto_resumo or "")

        lf = get_client()
        model_id = getattr(getattr(self.contexto_agent, "model", None), "id", "unknown")
        with lf.start_as_current_generation(
            name="FeedbackWorkflow.llm",
            model=model_id,
            input=full_prompt
        ) as gen:
            resp = (self.contexto_agent.run(full_prompt).content or "").strip()
            gen.update(output=resp)

        m = re.search(r"(?:contexto:\s*)?\b(Chatbot|Dashboard|Settings)\b", resp, re.IGNORECASE)
        return m.group(1).title() if m else ""

    def _sanitize_brackets(self, s: str) -> str:
        import re as _re
        return _re.sub(r"^\s*\[|\]\s*$", "", (s or "").strip())

    @observe(name="FeedbackWorkflow.executar", capture_input=True, capture_output=True)
    def executar(self, entrada: Dict):
        texto_resumo = (entrada.get("texto_resumo") or "").strip()
        if not texto_resumo:
            logger.warning("Sem resumo para gerar feedback.")
            return {"feedback_texto": "", "feedback_campos": {}}

        titulo_feedback = self._sanitize_brackets(entrada.get("assunto_principal") or "")
        comentario_cliente = self._sanitize_brackets(entrada.get("descricao_breve") or "")

        pref = (entrada.get("preferencia_contexto") or "").strip().title()
        if pref in {"Chatbot", "Dashboard", "Settings"}:
            contexto = pref
        else:
            contexto = self._extrair_contexto_com_llm(texto_resumo) or ""

        feedback_resp = (
            f"titulo_feedback: {titulo_feedback}\n"
            f"comentario_cliente: {comentario_cliente}\n"
            f"contexto: {contexto}"
        ).strip()

        campos = self._extrair_campos_feedback(feedback_resp)

        sess = make_session()
        feedback_webhook_url = self.settings.WEBHOOK_FEEDBACK_URL
        if feedback_webhook_url and (feedback_resp or any(v for v in campos.values())):
            try:
                sess.post(str(feedback_webhook_url), json={
                    "feedback_texto": feedback_resp,
                    "feedback_campos": campos
                }, timeout=6).raise_for_status()
            except Exception as e:
                logger.error(f"Falha ao enviar FEEDBACK para webhook: {e}")

        return {"feedback_texto": feedback_resp, "feedback_campos": campos}

    def _extrair_campos_feedback(self, texto: str):
        padroes = {
            "titulo_feedback": r"titulo_feedback:\s*(.*)",
            "comentario_cliente": r"comentario_cliente:\s*(.*)",
            "contexto": r"contexto:\s*(Chatbot|Dashboard|Settings)"
        }
        out = {}
        import re as _re
        for k, p in padroes.items():
            m = _re.search(p, texto, _re.IGNORECASE)
            out[k] = m.group(1).strip() if m else ""

        ctx = out.get("contexto", "").title()
        if ctx not in {"Chatbot", "Dashboard", "Settings"}:
            ctx = ""
        out["contexto"] = ctx
        return out
