from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.routers import flights_router

# Crear la aplicación FastAPI
app = FastAPI(
    title="[Bsale Challenge] Flight Check-in API",
    description="API para simulación de check-in de vuelos con asignación automática de asientos",
    version="1.0.0"
)

# Incluir los routers
app.include_router(flights_router, tags=["flights"])

@app.get("/")
async def root():
    return {"message": "[Bsale Challenge] Flight Check-in API is running - Test GitHub Actions v2"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Verifica la conexión a la base de datos"""
    try:
        # Ejecutar una query simple para verificar conexión
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}