from .auth import router as auth_router
from .test import router as test_router


__all__ = ["auth_router", "test_router"]