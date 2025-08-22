import os
import pandas as pd
import json
from datetime import datetime
from prefect import flow, task
from sqlalchemy import create_engine, text
from .config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear carpetas necesarias
os.makedirs("backups", exist_ok=True)
os.makedirs("logs", exist_ok=True)


@task
def extract_data():
    """Extrae datos de las tablas principales"""
    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Extraer contactos
            contactos_df = pd.read_sql("SELECT * FROM contactos", conn)
            programas_df = pd.read_sql("SELECT * FROM programas", conn)

            logger.info(f"Extraídos {len(contactos_df)} contactos y {len(programas_df)} programas")

            return {
                "contactos": contactos_df,
                "programas": programas_df,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error en extracción: {e}")
        raise


@task
def transform_data(raw_data):
    """Transforma y limpia los datos"""
    stats = {
        "timestamp": raw_data["timestamp"],
        "contactos": {
            "original": 0,
            "cleaned": 0,
            "removed": 0
        },
        "programas": {
            "original": 0,
            "cleaned": 0,
            "removed": 0
        }
    }

    # Limpiar contactos
    contactos_df = raw_data["contactos"].copy()
    stats["contactos"]["original"] = len(contactos_df)

    # Remover duplicados por correo
    original_count = len(contactos_df)
    contactos_df = contactos_df.drop_duplicates(subset=['correo'])
    stats["contactos"]["removed"] += original_count - len(contactos_df)

    # Limpiar correos inválidos (validación básica)
    contactos_df = contactos_df[contactos_df['correo'].str.contains('@', na=False)]

    # Normalizar nombres (capitalizar)
    contactos_df['nombre'] = contactos_df['nombre'].str.title().str.strip()

    # Remover mensajes vacíos o muy cortos
    contactos_df = contactos_df[contactos_df['mensaje'].str.len() >= 10]

    stats["contactos"]["cleaned"] = len(contactos_df)

    # Limpiar programas
    programas_df = raw_data["programas"].copy()
    stats["programas"]["original"] = len(programas_df)

    # Remover duplicados por nombre
    original_count = len(programas_df)
    programas_df = programas_df.drop_duplicates(subset=['nombre'])
    stats["programas"]["removed"] += original_count - len(programas_df)

    # Normalizar nombres de programas
    programas_df['nombre'] = programas_df['nombre'].str.title().str.strip()

    # Limpiar descripciones vacías
    programas_df = programas_df[programas_df['descripcion'].str.len() >= 20]

    stats["programas"]["cleaned"] = len(programas_df)

    logger.info(f"Transformación completada: {stats}")

    return {
        "contactos_clean": contactos_df,
        "programas_clean": programas_df,
        "stats": stats
    }


@task
def load_data(transformed_data):
    """Carga los datos limpios en tablas cleaned"""
    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Crear tablas cleaned si no existen
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS contactos_cleaned LIKE contactos
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS programas_cleaned LIKE programas
            """))

            # Limpiar tablas antes de insertar
            conn.execute(text("TRUNCATE TABLE contactos_cleaned"))
            conn.execute(text("TRUNCATE TABLE programas_cleaned"))

            # Cargar datos limpios
            transformed_data["contactos_clean"].to_sql(
                "contactos_cleaned",
                conn,
                if_exists="append",
                index=False
            )

            transformed_data["programas_clean"].to_sql(
                "programas_cleaned",
                conn,
                if_exists="append",
                index=False
            )

            conn.commit()

        logger.info("Datos cargados exitosamente en tablas cleaned")
        return True

    except Exception as e:
        logger.error(f"Error en carga: {e}")
        raise


@task
def create_backup(transformed_data):
    """Crea backup en CSV y logs del proceso"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Crear backups CSV
    contactos_backup = f"backups/contactos_backup_{timestamp}.csv"
    programas_backup = f"backups/programas_backup_{timestamp}.csv"

    transformed_data["contactos_clean"].to_csv(contactos_backup, index=False)
    transformed_data["programas_clean"].to_csv(programas_backup, index=False)

    # Crear log del proceso
    log_file = f"logs/etl_log_{timestamp}.json"
    with open(log_file, 'w') as f:
        json.dump(transformed_data["stats"], f, indent=2)

    logger.info(f"Backup creado: {contactos_backup}, {programas_backup}")
    logger.info(f"Log creado: {log_file}")

    return {
        "contactos_backup": contactos_backup,
        "programas_backup": programas_backup,
        "log_file": log_file
    }


@flow(name="fitness-etl-pipeline")
def fitness_etl_pipeline():
    """Pipeline ETL completo para datos fitness"""
    logger.info("Iniciando pipeline ETL Fitness")

    # Extract
    raw_data = extract_data()

    # Transform
    transformed_data = transform_data(raw_data)

    # Load
    load_success = load_data(transformed_data)

    # Backup
    backup_info = create_backup(transformed_data)

    logger.info("Pipeline ETL completado exitosamente")

    return {
        "status": "success",
        "stats": transformed_data["stats"],
        "backups": backup_info
    }


if __name__ == "__main__":
    # Ejecutar el pipeline
    result = fitness_etl_pipeline()
    print("Pipeline ETL ejecutado:", result)