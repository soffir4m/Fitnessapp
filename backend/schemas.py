from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


# Schemas para Contacto
class ContactoBase(BaseModel):
    nombre: str
    correo: EmailStr
    mensaje: str

    @validator('nombre')
    def validate_nombre(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip()

    @validator('mensaje')
    def validate_mensaje(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('El mensaje debe tener al menos 10 caracteres')
        return v.strip()


class ContactoCreate(ContactoBase):
    pass


class ContactoOut(ContactoBase):
    id_contacto: int
    fecha_envio: datetime

    class Config:
        from_attributes = True


# Schemas para Programa
class ProgramaBase(BaseModel):
    nombre: str
    descripcion: str

    @validator('nombre')
    def validate_nombre(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('El nombre del programa debe tener al menos 3 caracteres')
        return v.strip()

    @validator('descripcion')
    def validate_descripcion(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('La descripción debe tener al menos 10 caracteres')
        return v.strip()


class ProgramaCreate(ProgramaBase):
    pass


class ProgramaOut(ProgramaBase):
    id_programa: int

    class Config:
        from_attributes = True


# Schemas para APIs Externas

# Weather API Schemas
class WeatherResponse(BaseModel):
    ciudad: str
    temperatura: float
    sensacion_termica: float
    humedad: int
    descripcion: str
    viento: float
    recomendacion_ejercicio: str
    error: Optional[str] = None


# Nutrition API Schemas
class RecetaFitness(BaseModel):
    id: str
    nombre: str
    imagen: str
    tags_fitness: str


class NutritionResponse(BaseModel):
    categoria: str
    total_recetas: int
    recetas: List[RecetaFitness]
    error: Optional[str] = None
