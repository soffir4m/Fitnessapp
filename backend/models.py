from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Contacto(Base):
    __tablename__ = "contactos"

    id_contacto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_envio = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Contacto(id={self.id_contacto}, nombre='{self.nombre}', correo='{self.correo}')>"


class Programa(Base):
    __tablename__ = "programas"

    id_programa = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Programa(id={self.id_programa}, nombre='{self.nombre}')>"


class ContactoPrograma(Base):
    __tablename__ = "contacto_programa"

    id_contacto = Column(Integer, ForeignKey("contactos.id_contacto", ondelete="CASCADE"), primary_key=True)
    id_programa = Column(Integer, ForeignKey("programas.id_programa", ondelete="CASCADE"), primary_key=True)

    # Relaciones
    contacto = relationship("Contacto")
    programa = relationship("Programa")