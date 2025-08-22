import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# 🔹 Cargar variables del archivo .env automáticamente
load_dotenv()


class Settings(BaseSettings):
    # Base de datos
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "fitnessuser"        # Usuario MySQL
    DB_PASSWORD: str = "userpassword"   # Contraseña MySQL
    DB_NAME: str = "fitness"

    # APIs externas
    OPENWEATHER_API_KEY: Optional[str] = None  # ✅ Ahora sí se carga desde .env

    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    # Configuración de ETL
    BACKUP_RETENTION_DAYS: int = 30
    ETL_SCHEDULE_HOUR: int = 2

    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "./logs/app.log"

    @property
    def DATABASE_URL(self) -> str:
        """Genera la URL de conexión a MySQL"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = "../.env"  # 🔹 Archivo de variables
        case_sensitive = True
        extra = "allow"           # Permitir variables extra del .env


# Crear instancia global de configuración
settings = Settings()

# 🔹 Debug opcional (puedes borrar esto en producción)
print(f"DEBUG - OpenWeather API Key: {settings.OPENWEATHER_API_KEY}")
