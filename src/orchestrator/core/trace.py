from src.orchestrator.core.logging import logger
from src.orchestrator.config.settings import get_settings
from langfuse import Langfuse

def lf_client():
    settings = get_settings()
    lf = Langfuse(
    secret_key=settings.LANGFUSE_SECRET_KEY,
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    host=settings.LANGFUSE_HOST
    )
    try:
        if lf.auth_check():
            logger.info("Langfuse autenticado.")
        else:
            logger.warning("Langfuse NÃO autenticado. Verifique LANGFUSE_PUBLIC_KEY/SECRET_KEY/HOST.")
    except Exception as e:
        logger.error(f"Falha ao checar Langfuse: {e}")
    return lf