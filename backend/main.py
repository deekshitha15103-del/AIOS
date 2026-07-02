from fastapi import FastAPI

from backend.api.routes import router
from backend.core.config import settings
from backend.core.database import initialize_database
from backend.core.exceptions import AIOSException, aios_exception_handler


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)


@app.on_event("startup")
def startup_event():
    initialize_database()


app.add_exception_handler(AIOSException, aios_exception_handler)

app.include_router(router, prefix="/api/v1")