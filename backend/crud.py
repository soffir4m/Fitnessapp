from sqlalchemy.orm import Session
import models, schemas

# Contactos
def create_contacto(db: Session, contacto: schemas.ContactoCreate):
    db_contacto = models.Contacto(**contacto.dict())
    db.add(db_contacto)
    db.commit()
    db.refresh(db_contacto)
    return db_contacto

def get_contactos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Contacto).offset(skip).limit(limit).all()

# Programas
def create_programa(db: Session, programa: schemas.ProgramaCreate):
    db_programa = models.Programa(**programa.dict())
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    return db_programa

def get_programas(db: Session):
    return db.query(models.Programa).all()
