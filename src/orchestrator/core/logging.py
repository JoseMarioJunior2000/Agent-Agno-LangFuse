import logging

logger = logging.getLogger("orchestrator")
handler = logging.StreamHandler()
fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.INFO)