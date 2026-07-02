from fastapi import APIRouter

from backend.core.exceptions import AIOSException
from backend.core.health import health_check
from backend.core.logger import get_logger
from backend.modules.knowledge.api import router as knowledge_router
from backend.schemas.common import APIResponse


router = APIRouter()
router.include_router(knowledge_router)

logger = get_logger(__name__)


@router.get("/", response_model=APIResponse)
def root():
    logger.info("Root endpoint called")

    return APIResponse(
        success=True,
        message="AIOS backend is running",
        data={
            "name": "AIOS",
            "description": "The Open Enterprise AI Operating System",
            "status": "running",
        },
    )


@router.get("/health", response_model=APIResponse)
def health():
    logger.info("Health endpoint called")

    return APIResponse(
        success=True,
        message="Health check successful",
        data=health_check(),
    )


@router.get("/test-error")
def test_error():
    raise AIOSException(
        message="This is a test AIOS error",
        status_code=400,
    )