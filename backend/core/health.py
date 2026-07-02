from backend.core.config import settings
from backend.schemas.health import HealthResponse


def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
    )