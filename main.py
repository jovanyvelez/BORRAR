
from fastapi import FastAPI


# Importar configuración
from src.config import settings

# Importar rutas
from src.routes import auth_router, apartamentos_router


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)



app.include_router(auth_router)
app.include_router(apartamentos_router)

