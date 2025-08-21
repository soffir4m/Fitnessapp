from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, Base, get_db
from external_apis import weather_service, nutrition_service

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitness API", version="1.0", description="API para gestión fitness con integración externa")

# Rutas de programas
@app.post("/programas/", response_model=schemas.ProgramaOut)
def crear_programa(programa: schemas.ProgramaCreate, db: Session = Depends(get_db)):
    return crud.create_programa(db, programa)

@app.get("/programas/", response_model=list[schemas.ProgramaOut])
def listar_programas(db: Session = Depends(get_db)):
    return crud.get_programas(db)

# Rutas de contactos
@app.post("/contactos/", response_model=schemas.ContactoOut)
def crear_contacto(contacto: schemas.ContactoCreate, db: Session = Depends(get_db)):
    return crud.create_contacto(db, contacto)

@app.get("/contactos/", response_model=list[schemas.ContactoOut])
def listar_contactos(db: Session = Depends(get_db)):
    return crud.get_contactos(db)

# Rutas de API externa
@app.get("/clima-entrenamiento/")
async def obtener_clima_entrenamiento(ciudad: str = "San Jose"):
    """Obtiene información del clima con recomendaciones para entrenar"""
    clima = await weather_service.get_weather(ciudad)
    if "error" in clima:
        raise HTTPException(status_code=400, detail=clima["error"])
    return clima

@app.get("/recetas-fitness/")
async def obtener_recetas_fitness(categoria: str = "Chicken"):
    """Obtiene recetas saludables para complementar el entrenamiento"""
    recetas = await nutrition_service.get_healthy_meals(categoria)
    if "error" in recetas:
        raise HTTPException(status_code=400, detail=recetas["error"])
    return recetas

@app.get("/")
def root():
    return {"message": "Fitness API funcionando", "docs": "/docs"}