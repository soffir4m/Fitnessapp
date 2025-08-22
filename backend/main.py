from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, Base, get_db, test_connection
from .external_apis import weather_service, nutrition_service
import logging
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear las tablas
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tablas creadas/verificadas exitosamente")
except Exception as e:
    logger.error(f"❌ Error creando tablas: {e}")

app = FastAPI(
    title="Fitness API",
    version="1.0",
    description="API para gestión fitness con integración externa"
)

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"  # Solo para desarrollo, remover en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de manejo de errores
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Error no manejado en {request.url}: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

# Endpoint de salud
@app.get("/health")
def health_check():
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "message": "Fitness API funcionando"
    }

# Rutas de programas
@app.post("/programas/", response_model=schemas.ProgramaOut)
def crear_programa(programa: schemas.ProgramaCreate, db: Session = Depends(get_db)):
    logger.info(f"🔄 Creando programa: {programa.nombre}")
    return crud.create_programa(db, programa)

@app.get("/programas/", response_model=list[schemas.ProgramaOut])
def listar_programas(db: Session = Depends(get_db)):
    logger.info("📋 Listando todos los programas")
    return crud.get_programas(db)

@app.get("/programas/{programa_id}", response_model=schemas.ProgramaOut)
def obtener_programa(programa_id: int, db: Session = Depends(get_db)):
    logger.info(f"🔍 Buscando programa con ID: {programa_id}")
    return crud.get_programa_by_id(db, programa_id)

# Rutas de contactos
@app.post("/contactos/", response_model=schemas.ContactoOut)
def crear_contacto(contacto: schemas.ContactoCreate, db: Session = Depends(get_db)):
    logger.info(f"🔄 Creando contacto: {contacto.nombre} - {contacto.correo}")
    try:
        resultado = crud.create_contacto(db, contacto)
        logger.info(f"✅ Contacto creado exitosamente con ID: {resultado.id_contacto}")
        return resultado
    except Exception as e:
        logger.error(f"❌ Error en endpoint crear_contacto: {e}")
        raise

@app.get("/contactos/", response_model=list[schemas.ContactoOut])
def listar_contactos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    logger.info(f"📋 Listando contactos (skip={skip}, limit={limit})")
    return crud.get_contactos(db, skip=skip, limit=limit)

@app.get("/contactos/{contacto_id}", response_model=schemas.ContactoOut)
def obtener_contacto(contacto_id: int, db: Session = Depends(get_db)):
    logger.info(f"🔍 Buscando contacto con ID: {contacto_id}")
    return crud.get_contacto_by_id(db, contacto_id)

# Rutas de APIs Externas
@app.get("/weather/", response_model=schemas.WeatherResponse)
async def obtener_clima(ciudad: str = "San Jose"):
    """Obtiene información del clima y recomendaciones de ejercicio"""
    logger.info(f"🌤️ Obteniendo clima para: {ciudad}")
    try:
        resultado = await weather_service.get_weather(ciudad)
        if "error" in resultado:
            logger.warning(f"⚠️ Error en API del clima: {resultado['error']}")
        else:
            logger.info(f"✅ Clima obtenido: {resultado['temperatura']}°C, {resultado['descripcion']}")
        return resultado
    except Exception as e:
        logger.error(f"❌ Error obteniendo clima: {e}")
        return {"error": f"Error interno: {str(e)}"}

@app.get("/nutrition/", response_model=schemas.NutritionResponse)
async def obtener_recetas_fitness(categoria: str = "Chicken"):
    """Obtiene recetas saludables por categoría para complementar rutinas fitness"""
    logger.info(f"🍽️ Obteniendo recetas fitness para categoría: {categoria}")
    try:
        resultado = await nutrition_service.get_healthy_meals(categoria)
        if "error" in resultado:
            logger.warning(f"⚠️ Error en API de nutrición: {resultado['error']}")
        else:
            logger.info(f"✅ Recetas obtenidas: {resultado['total_recetas']} recetas de {categoria}")
        return resultado
    except Exception as e:
        logger.error(f"❌ Error obteniendo recetas: {e}")
        return {"error": f"Error interno: {str(e)}", "categoria": categoria, "total_recetas": 0, "recetas": []}

@app.get("/fitness-dashboard/")
async def obtener_dashboard_fitness(ciudad: str = "San Jose", categoria_comida: str = "Chicken"):
    """Endpoint combinado que obtiene clima y recetas para un dashboard fitness completo"""
    logger.info(f"📊 Generando dashboard fitness - Ciudad: {ciudad}, Comida: {categoria_comida}")
    try:
        # Llamar ambas APIs de forma concurrente
        clima_task = weather_service.get_weather(ciudad)
        recetas_task = nutrition_service.get_healthy_meals(categoria_comida)
        
        clima, recetas = await clima_task, await recetas_task
        
        dashboard = {
            "ubicacion": ciudad,
            "clima": clima,
            "recetas_fitness": recetas,
            "recomendacion_general": f"Hoy es un día perfecto para entrenar en {ciudad}. Te sugerimos probar algunas recetas de {categoria_comida}."
        }
        
        logger.info(f"✅ Dashboard generado exitosamente para {ciudad}")
        return dashboard
        
    except Exception as e:
        logger.error(f"❌ Error generando dashboard: {e}")
        return {
            "ubicacion": ciudad,
            "error": f"Error generando dashboard: {str(e)}",
            "clima": {"error": "No disponible"},
            "recetas_fitness": {"error": "No disponible", "categoria": categoria_comida, "total_recetas": 0, "recetas": []},
            "recomendacion_general": "Dashboard temporalmente no disponible"
        }

@app.get("/")
def root():
    return {"message": "Fitness API funcionando", "docs": "/docs", "health": "/health"}

# Startup event para verificar conexión
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando Fitness API...")
    if test_connection():
        logger.info("✅ API iniciada correctamente")
    else:
        logger.error("❌ Problemas con la conexión a la base de datos")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)