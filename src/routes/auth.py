from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, APIRouter, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

from src.models import db_manager, Usuario
from src.dependencies import templates

# Configuración JWT
SECRET_KEY = "20673b779bd404ac9cdc034d0e84f27f60401df8854506e317317940be725648"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_email(session: Session, email: str) -> Usuario | None:
    """Obtener usuario por email desde la base de datos"""
    statement = select(Usuario).where(Usuario.email == email)
    return session.exec(statement).first()


def authenticate_user(session: Session, email: str, password: str):
    """Autenticar usuario con email y contraseña"""
    user = get_user_by_email(session, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_from_token(token: str, session: Session) -> Optional[Usuario]:
    """Obtener usuario actual desde el token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
        
        user = get_user_by_email(session, email)
        return user if user and user.is_active else None
    except InvalidTokenError:
        return None


async def get_current_user_optional(request: Request, session: Session = Depends(db_manager.get_session)) -> Optional[Usuario]:
    """Dependency opcional para obtener el usuario actual - no lanza excepción si no hay token"""
    token = request.cookies.get("access_token")
    
    if not token:
        # También intentar desde Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return None
    
    return get_current_user_from_token(token, session)


async def get_current_user(request: Request, session: Session = Depends(db_manager.get_session)):
    """Dependency para obtener el usuario actual desde cookie o header"""
    token = request.cookies.get("access_token")
    
    if not token:
        # También intentar desde Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_current_user_from_token(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: Optional[Usuario] = Depends(get_current_user_optional)):
    """Página principal - redirige a login si no está autenticado"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("welcome.html", {
        "request": request,
        "user": current_user
    })


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Mostrar página de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(db_manager.get_session)
):
    """Procesar login de usuario"""
    user = authenticate_user(session, email, password)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email o contraseña incorrectos"
        })
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    # Redirigir a la página de bienvenida con cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False  # En producción debería ser True con HTTPS
    )
    
    return response


@router.get("/logout")
async def logout():
    """Cerrar sesión del usuario"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@router.post("/token")
async def login_for_access_token(
    session: Annotated[Session, Depends(db_manager.get_session)],
    email: str = Form(...),
    password: str = Form(...)
) -> Token:
    """Endpoint para obtener token JWT (para API)"""
    user = authenticate_user(session, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


