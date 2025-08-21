from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Contacto(Base):
    __tablename__ = "contactos"

    id_contacto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_envio = Column(TIMESTAMP, server_default=func.now())

    programas = relationship("ContactoPrograma", back_populates="contacto")

class Programa(Base):
    __tablename__ = "programas"

    id_programa = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=False)

    contactos = relationship("ContactoPrograma", back_populates="programa")

class ContactoPrograma(Base):
    __tablename__ = "contacto_programa"

    id_contacto = Column(Integer, ForeignKey("contactos.id_contacto"), primary_key=True)
    id_programa = Column(Integer, ForeignKey("programas.id_programa"), primary_key=True)

    contacto = relationship("Contacto", back_populates="programas")
    programa = relationship("Programa", back_populates="contactos")
