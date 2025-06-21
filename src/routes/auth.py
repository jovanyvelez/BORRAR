from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from src.models import db_manager, Usuario
from src.dependencies import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página de login"""

    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    try:

        """Procesar login de usuario"""
        with db_manager.get_session() as session:
            user = session.exec(
                select(Usuario).where(Usuario.username == username)
            ).first()
            print(f"Usuario encontrado: {user}")
            
            if not user or user.hashed_password != password:
                return templates.TemplateResponse(
                    "login.html", 
                    {
                        "request": request, 
                        "error": "Usuario o contraseña incorrectos"
                    }
                )
        
            
            # Redirigir según el rol
        return {"success": True}
    except Exception as e:
        print(f"Error en el login: {e}")
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "error": "Ocurrió un error al procesar el login"
            }
        )

@router.get("/logout")
async def logout(request: Request):
    """Cerrar sesión"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)