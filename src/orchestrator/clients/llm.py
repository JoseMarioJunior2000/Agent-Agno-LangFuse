from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
import logging
import requests
from orchestrator.config.settings import get_settings

log = logging.getLogger("llm_validation")

def make_agent(name: str, system_instructions: str, api_key: str, model_id: str = "gpt-4o-mini") -> Agent:
    settings = get_settings()
    return _probe(name, system_instructions, api_key, model_id, settings)

def _probe(name: str, system_instructions: str, api_key: str, model_id: str, settings) -> Agent:
    """
    Valida primeiro o OpenAI. Se falhar, usa Gemini.
    Retorna um Agent pronto para uso.
    """
    try:
        return validation_primary_llm(name, system_instructions, settings.OPENAI_API_KEY, model_id)
    except Exception as e:
        log.warning(f"OpenAI indisponível: {e}. Usando fallback Gemini.")
        return llm_fallback(name, system_instructions, settings.GEMINI_API_KEY, "gemini-2.0-flash")

def validation_primary_llm(name: str, system_instructions: str, api_key: str, model_id: str) -> Agent:
    """ Valida chamando endpoint público de modelos da OpenAI """
    resp = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=5,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI não validado: {resp.status_code} {resp.text}")

    return Agent(
        name=name,
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=system_instructions,
    )


def llm_fallback(name: str, system_instructions: str, api_key: str, model_id: str) -> Agent:
    """ Valida chamando endpoint de modelos da Gemini """
    resp = requests.get(
        "https://generativelanguage.googleapis.com/v1/models",
        params={"key": api_key},
        timeout=5,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini não validado: {resp.status_code} {resp.text}")

    return Agent(
        name=name,
        model=Gemini(id=model_id, api_key=api_key),
        instructions=system_instructions,
    )

