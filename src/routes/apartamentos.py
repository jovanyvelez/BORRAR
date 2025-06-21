from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from src.models import db_manager, Apartamento, Propietario, Usuario
from src.dependencies import templates

router = APIRouter()

@router.get("/apartamentos", response_class=HTMLResponse)
async def mostrar_apartamentos(
    request: Request, 
    session: Session = Depends(db_manager.get_session)
):
    """Muestra todos los apartamentos con sus propietarios - requiere autenticación"""
    
    # Verificar autenticación manualmente para mejor manejo de errores
    from .auth import get_current_user_optional
    current_user = await get_current_user_optional(request, session)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Consulta para obtener apartamentos con sus propietarios
    statement = select(Apartamento).join(Propietario, isouter=True)
    apartamentos = session.exec(statement).all()
    
    # Calcular estadísticas
    total_apartamentos = len(apartamentos)
    apartamentos_con_propietario = sum(1 for apt in apartamentos if apt.propietario is not None)
    apartamentos_sin_propietario = total_apartamentos - apartamentos_con_propietario
    
    return templates.TemplateResponse("apartamentos.html", {
        "request": request,
        "apartamentos": apartamentos,
        "total_apartamentos": total_apartamentos,
        "apartamentos_con_propietario": apartamentos_con_propietario,
        "apartamentos_sin_propietario": apartamentos_sin_propietario,
        "user": current_user
    })
