from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Configuración del engine con opciones específicas para MySQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=False  # Cambiar a True para debug SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para probar la conexión
def test_connection():
    try:
        with engine.connect() as connection:
            logger.info("✅ Conexión a base de datos exitosa")
            return True
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        return False