# Agent Orquestrador de Atendimento

Orquestrador de fluxos inteligentes, responsável por processar conversas com clientes e gerar automaticamente **resumos estruturados**, **feedbacks contextuais** e **classificações de tarefas**.
O projeto utiliza **FastAPI**, **Agno/LLM Agents** e **Langfuse** para rastreamento detalhado de execuções.

---

## 🚀 Visão Geral

Este serviço expõe uma API de orquestração de **workflows** em três estágios principais:

1. **Resumo (SummaryWorkflow)** → extrai dados estruturados de uma conversa
2. **Feedback (FeedbackWorkflow)** → gera feedback e contexto (Chatbot, Dashboard, etc.)
3. **Classificação (ClassifierWorkflow)** → define tipo de tarefa, prioridade e projeto correspondente

Cada etapa é executada por um agente LLM específico (via **Agno**) e registrada no **Langfuse**, garantindo observabilidade completa — desde o prompt até o resultado.

---

## 🧩 Arquitetura

```
FastAPI API  ->  AtendimentoWorkflow  ->  Workflows (Resumo, Feedback, Classificação)
                     │
                     └──► Webhooks (resumo, feedback, tarefa)

Logs, traces e generations -> Langfuse (observabilidade e monitoramento)
```

---

## 🔧 Stack Técnica

| Componente         | Descrição                        |
| ------------------ | -------------------------------- |
| **FastAPI**        | Framework backend (API REST)     |
| **Agno**           | Abstração de agentes LLM         |
| **OpenAI**         | Modelo base (`gpt-4o-mini`)      |
| **Langfuse**       | Observabilidade de LLMs e fluxos |

---

## ⚙️ Instalação (Ambiente Local)

### 1️⃣ Clonar o repositório

```bash
git clone 
cd Agent-Agno-LangFuse
```

### 2️⃣ Criar ambiente virtual

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows PowerShell
# ou
source .venv/bin/activate       # Linux/Mac
```

### 3️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente `.env`

```bash
OPENAI_API_KEY=
WEBHOOK_RESUMO_URL=
WEBHOOK_FEEDBACK_URL=
WEBHOOK_CATEGORIA_URL=

LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=
```

### 5️⃣ Executar o servidor

```bash
uvicorn orchestrator.main:app --reload --port 8000 --app-dir src
```

Acesse a documentação Swagger em:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧠 Workflows disponíveis

| Endpoint                          | Descrição                                                    |
| --------------------------------- | ------------------------------------------------------------ |
| `POST /api/workflows/atendimento` | Executa o fluxo completo (Resumo → Feedback → Classificação) |
| `GET /health`                     | Verifica se o serviço está ativo                             |

### Exemplo de requisição

```json
{
  "nome": "Gabriela Nogueira",
  "email": "gabriela.nogueira@clinicaprimavera.com",
  "telefone": "(11) 91234-5678",
  "conversa": "Cliente: Quero sugerir uma melhoria..."
}
```

---

## 📊 Observabilidade com Langfuse

Cada chamada ao agente ou workflow é rastreada no **Langfuse** com:

* **Trace** → identifica o fluxo (`workflows.atendimento`)
* **Span** → cada etapa (`SummaryWorkflow`, `FeedbackWorkflow`, etc.)
* **Generation** → chamadas LLM (`gpt-4o-mini`) com `prompt`, `system`, `output`

### Exemplo de instrumentação

```python
from langfuse import observe, get_client

@observe(name="SummaryWorkflow.executar", capture_input=True, capture_output=True)
def executar(self, entrada: Dict):
    lf = get_client()
    with lf.start_as_current_generation(
        name="Resumo Estruturado.llm",
        model="gpt-4o-mini",
        input={"prompt": prompt, "system": SUMMARY_AGENT_INSTRUCTION},
        metadata={"agent_name": "Resumo Estruturado"}
    ) as gen:
        out = self.resumo_agent.run(prompt).content.strip()
        gen.update(output=out)
```

---

## 🧾 Estrutura de Pastas

```
src/
 └── orchestrator/
     ├── api/               # Rotas e dependências FastAPI
     ├── clients/           # Clients HTTP e LLM
     ├── config/            # Configurações e settings (dotenv)
     ├── core/              # Logging e trace
     ├── prompts/           # Instruções de agentes
     ├── workflows/         # Workflows (Resumo, Feedback, Classificação)
     ├── main.py            # App principal FastAPI
     └── scripts/           # utilitários (start.ps1, run.sh, etc.)
```

---

## 🧪 Teste rápido

```bash
curl -X POST http://localhost:8000/api/workflows/atendimento \
  -H "Content-Type: application/json" \
  -d '{
        "nome": "Gabriela Nogueira",
        "email": "gabriela.nogueira@clinicaprimavera.com",
        "telefone": "(11) 91234-5678",
        "conversa": "Cliente: O bot do whatsapp não está me respodendo."
      }'
```

---

## Autor

© José Mário
Contato: jmsjunior2000@hotmail.com
