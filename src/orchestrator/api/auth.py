from fastapi import HTTPException
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.orchestrator.config.settings import get_settings

bearer = HTTPBearer(auto_error=False)

def require_api_key():
    async def dep(creds: HTTPAuthorizationCredentials = Depends(bearer)):
        if not creds:
            raise HTTPException(401, "Missing Authorization")
        provided = creds.credentials
        settings = get_settings()
        if provided != settings.WORKFLOWS_API_KEY:
            raise HTTPException(401, "Invalid API key")
        return True
    return dep