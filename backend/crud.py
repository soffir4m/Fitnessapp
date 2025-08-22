from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from . import models, schemas
import logging

logger = logging.getLogger(__name__)


# Contactos
def create_contacto(db: Session, contacto: schemas.ContactoCreate):
    try:
        # Crear el objeto con los datos del schema
        db_contacto = models.Contacto(
            nombre=contacto.nombre,
            correo=contacto.correo,
            mensaje=contacto.mensaje
        )

        db.add(db_contacto)
        db.commit()
        db.refresh(db_contacto)

        logger.info(f"✅ Contacto creado exitosamente: ID {db_contacto.id_contacto}, Nombre: {db_contacto.nombre}")
        return db_contacto

    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ Error de integridad al crear contacto: {e}")
        if "correo" in str(e).lower():
            raise HTTPException(status_code=400, detail="Ya existe un contacto con ese correo electrónico")
        raise HTTPException(status_code=400, detail="Error de integridad en los datos")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ Error de SQLAlchemy: {e}")
        raise HTTPException(status_code=500, detail="Error en la base de datos")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error inesperado al crear contacto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


def get_contactos(db: Session, skip: int = 0, limit: int = 10):
    try:
        contactos = db.query(models.Contacto).offset(skip).limit(limit).all()
        logger.info(f"📋 Obtenidos {len(contactos)} contactos (skip={skip}, limit={limit})")
        return contactos
    except Exception as e:
        logger.error(f"❌ Error al obtener contactos: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener contactos")


def get_contacto_by_id(db: Session, contacto_id: int):
    try:
        contacto = db.query(models.Contacto).filter(models.Contacto.id_contacto == contacto_id).first()
        if not contacto:
            logger.warning(f"⚠️ Contacto no encontrado con ID: {contacto_id}")
            raise HTTPException(status_code=404, detail="Contacto no encontrado")

        logger.info(f"✅ Contacto encontrado: ID {contacto.id_contacto}")
        return contacto
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al buscar contacto {contacto_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar contacto")


# Programas
def create_programa(db: Session, programa: schemas.ProgramaCreate):
    try:
        # Crear el objeto con los datos del schema
        db_programa = models.Programa(
            nombre=programa.nombre,
            descripcion=programa.descripcion
        )

        db.add(db_programa)
        db.commit()
        db.refresh(db_programa)

        logger.info(f"✅ Programa creado exitosamente: ID {db_programa.id_programa}, Nombre: {db_programa.nombre}")
        return db_programa

    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ Error de integridad al crear programa: {e}")
        if "nombre" in str(e).lower():
            raise HTTPException(status_code=400, detail="Ya existe un programa con ese nombre")
        raise HTTPException(status_code=400, detail="Error de integridad en los datos")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ Error de SQLAlchemy: {e}")
        raise HTTPException(status_code=500, detail="Error en la base de datos")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error inesperado al crear programa: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


def get_programas(db: Session):
    try:
        programas = db.query(models.Programa).all()
        logger.info(f"📋 Obtenidos {len(programas)} programas")
        return programas
    except Exception as e:
        logger.error(f"❌ Error al obtener programas: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener programas")


def get_programa_by_id(db: Session, programa_id: int):
    try:
        programa = db.query(models.Programa).filter(models.Programa.id_programa == programa_id).first()
        if not programa:
            logger.warning(f"⚠️ Programa no encontrado con ID: {programa_id}")
            raise HTTPException(status_code=404, detail="Programa no encontrado")

        logger.info(f"✅ Programa encontrado: ID {programa.id_programa}")
        return programa
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al buscar programa {programa_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar programa")