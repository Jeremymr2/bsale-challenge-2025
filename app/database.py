# FILE: app/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Leer las credenciales de la base de datos desde las variables de entorno
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "test")

# Crear la URL de conexión
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Crear el motor de conexión con configuración optimizada
engine = create_engine(
    DATABASE_URL,
    # Pool de conexiones optimizado
    pool_size=5,
    max_overflow=10,
    pool_timeout=10,  # Reducido para respuesta más rápida
    pool_recycle=4,  # Reciclar conexiones cada 4 seg (antes de timeout del servidor)
    pool_pre_ping=True,  # Verificar conexión antes de usar
    # Configuración específica para MySQL optimizada
    connect_args={
        "autocommit": False,
        "connect_timeout": 5,  # Timeout más corto
        "read_timeout": 10,
        "write_timeout": 10,
    },
    # Configuración adicional para rendimiento
    echo=False,  # Desactivar logging SQL para mejor rendimiento
)

# Crear una sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()