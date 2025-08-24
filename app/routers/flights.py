from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import DisconnectionError, OperationalError
from typing import Union
from app.database import get_db
from app.models.models import Flight
from app.schemas.flight_schemas import (
    PassengerResponse,
    FlightDataResponse,
    FlightResponse,
    FlightNotFoundResponse,
    FlightErrorResponse
)

router = APIRouter()


@router.get("/flights/{flight_id}/passengers", 
           response_model=Union[FlightResponse, FlightNotFoundResponse, FlightErrorResponse])
async def get_flight_passengers(flight_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los pasajeros de un vuelo con asientos asignados mediante simulación de check-in.
    """
    try:
        # Verificar si el vuelo existe
        flight = db.query(Flight).filter(Flight.flight_id == flight_id).first()
        if not flight:
            return FlightNotFoundResponse()

        # Convertir a formato de respuesta (snake_case a camelCase) - Base
        passengers_data = []
        
        # Crear respuesta de datos del vuelo
        flight_data = FlightDataResponse(
            flight_id=flight.flight_id,
            takeoff_date_time=flight.takeoff_date_time,
            takeoff_airport=flight.takeoff_airport,
            landing_date_time=flight.landing_date_time,
            landing_airport=flight.landing_airport,
            airplane_id=flight.airplane_id,
            passengers=passengers_data
        )
        
        return FlightResponse(code=200, data=flight_data)
        
    except (DisconnectionError, OperationalError):
        return FlightErrorResponse(code=400, errors="could not connect to db")
    except Exception as e:
        return FlightErrorResponse(code=400, errors=f"could not connect to db: {str(e)}")