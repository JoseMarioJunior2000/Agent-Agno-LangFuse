from fastapi import APIRouter, Depends
from orchestrator.api.deps import get_settings_dep
from orchestrator.schemas.resumo import ResumoIn, ResumoOut
from orchestrator.schemas.feedback import FeedbackIn, FeedbackOut
from orchestrator.schemas.classificacao import ClassificacaoIn, ClassificacaoOut
from orchestrator.schemas.atendimento import AtendimentoIn, AtendimentoOut
from orchestrator.workflows.summary import SummaryWorkflow
from orchestrator.workflows.feedback import FeedbackWorkflow
from orchestrator.workflows.classifier import ClassifierWorkflow
from orchestrator.workflows.assistance import AssistanceWorkflow
from orchestrator.core.trace import lf_client
from orchestrator.config.settings import Settings

from orchestrator.api.auth import require_api_key
from langfuse import observe

router = APIRouter()
lf = lf_client()

@router.post(
    "/workflows/summary",
    response_model=ResumoOut,
    tags=["workflows"],
    dependencies=[Depends(require_api_key())],
)
def run_resumo(payload: ResumoIn, settings: Settings = Depends(get_settings_dep)):
    return SummaryWorkflow(settings).executar(payload.dict())

@router.post(
    "/workflows/feedback",
    response_model=FeedbackOut,
    tags=["workflows"],
    dependencies=[Depends(require_api_key())],
)
def run_feedback(payload: FeedbackIn, settings: Settings = Depends(get_settings_dep)):
    return FeedbackWorkflow(settings).executar(payload.dict())

@router.post(
    "/workflows/classification",
    response_model=ClassificacaoOut,
    tags=["workflows"],
    dependencies=[Depends(require_api_key())],
)
def run_classificar(payload: ClassificacaoIn, settings: Settings = Depends(get_settings_dep)):
    return ClassifierWorkflow(settings).executar(payload.dict())

@router.post(
    "/workflows/assistance",
    response_model=AtendimentoOut,
    tags=["workflows"],
    dependencies=[Depends(require_api_key())],
)
@observe(name="Orchestrator", capture_input=True, capture_output=True)
def run_atendimento(payload: AtendimentoIn, settings: Settings = Depends(get_settings_dep)):
    lf.update_current_trace(user_id=payload.email or None, tags=["fastapi","atendimento"])
    return AssistanceWorkflow(settings).executar(payload.dict())