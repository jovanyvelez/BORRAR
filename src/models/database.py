from dotenv import load_dotenv
import os
from sqlmodel import Session, create_engine

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
load_dotenv()

print(os.environ.get('DATABASE_URL'))
url_database = os.environ.get('DATABASE_URL')

if not url_database:
    raise ValueError("DATABASE_URL no está configurada en las variables de entorno")


engine = create_engine(url_database, echo=True)

class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine

 
    def get_session(self) -> Session:
        return Session(self.engine)

    def get_engine(self):
        return self.engine

# Instancia global del manager de base de datos
db_manager = DatabaseManager(engine)
