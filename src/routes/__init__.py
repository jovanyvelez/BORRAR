from .auth import router as auth_router
from .apartamentos import router as apartamentos_router

__all__ = ["auth_router", "apartamentos_router"]