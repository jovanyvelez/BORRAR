# Sistema de Administración de Apartamentos

Sistema web desarrollado con FastAPI y SQLModel para la gestión de apartamentos, propietarios y registros financieros.

## 🚀 Características

- **Gestión de Apartamentos**: Visualización completa de todos los apartamentos con sus propietarios
- **Modelos SQLModel**: Modelos completos para todas las tablas de la base de datos
- **Interfaz Web**: Plantilla Jinja2 responsive para mostrar los datos
- **API REST**: Endpoints para acceso programático a los datos
- **Base de datos PostgreSQL**: Conexión a Supabase

## 📋 Modelos Incluidos

- `Apartamento`: Información de apartamentos y coeficientes de copropiedad
- `Propietario`: Datos de propietarios
- `Usuario`: Sistema de usuarios con roles
- `Concepto`: Conceptos financieros
- `RegistroFinancieroApartamento`: Registros financieros por apartamento
- `GastoComunidad`: Gastos comunes del edificio
- `PresupuestoAnual` e `ItemPresupuesto`: Presupuestación
- `CuotaConfiguracion`: Configuración de cuotas
- `TasaInteresMora`: Tasas de interés por mora
- `ControlProcesamientoMensual`: Control de procesamiento

## 🛠️ Instalación

1. Instalar dependencias con uv:
```bash
uv install
```

2. Configurar variables de entorno en `.env`:
```
DATABASE_URL="postgresql://usuario:password@host:puerto/database"
```

3. Ejecutar la aplicación:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 📱 Endpoints

- `/` - Página principal con lista de apartamentos (HTML)
- `/api/apartamentos` - API para obtener apartamentos (JSON)

## 🎨 Características de la Interfaz

- **Diseño responsive** para móviles y escritorio
- **Búsqueda en tiempo real** por identificador, propietario o documento
- **Estadísticas** de apartamentos con/sin propietario
- **Tabla interactiva** con información detallada

## 🏗️ Estructura del Proyecto

```
├── main.py              # Aplicación FastAPI principal
├── models/              # Modelos SQLModel
│   └── __init__.py      # Todos los modelos de la BD
├── database.py          # Configuración de base de datos
├── templates/           # Plantillas Jinja2
│   └── apartamentos.html
├── .env                 # Variables de entorno
└── requirements.txt     # Dependencias
```

## 🔧 Tecnologías

- **FastAPI**: Framework web moderno para APIs
- **SQLModel**: ORM basado en Pydantic y SQLAlchemy
- **Jinja2**: Motor de plantillas
- **PostgreSQL**: Base de datos
- **Uvicorn**: Servidor ASGI