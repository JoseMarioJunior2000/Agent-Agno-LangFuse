#!/bin/bash
set -e  # Faz o script parar se ocorrer algum erro

# Ativa o ambiente virtual se ainda não estiver ativo
if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Inicia o servidor Uvicorn
python -m uvicorn orchestrator.main:app --reload --port 8000 --app-dir src