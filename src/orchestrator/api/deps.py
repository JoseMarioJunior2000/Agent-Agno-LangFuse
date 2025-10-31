from orchestrator.config.settings import get_settings
from typing import Generator

def get_settings_dep():
    return get_settings()
