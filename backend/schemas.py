from pydantic import BaseModel, EmailStr
from typing import List, Optional

class ContactoBase(BaseModel):
    nombre: str
    correo: EmailStr
    mensaje: str

class ContactoCreate(ContactoBase):
    pass

class ContactoOut(ContactoBase):
    id_contacto: int
    class Config:
        orm_mode = True

class ProgramaBase(BaseModel):
    nombre: str
    descripcion: str

class ProgramaCreate(ProgramaBase):
    pass

class ProgramaOut(ProgramaBase):
    id_programa: int
    class Config:
        orm_mode = True
