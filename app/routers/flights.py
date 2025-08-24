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
from app.services.seat_assignment import SeatAssignmentService

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
        
        # Simular asignación de asientos
        seat_service = SeatAssignmentService(db)
        boarding_passes = seat_service.assign_seats_for_flight(flight_id)
        
        # Si no hay boarding passes, retornar vuelo con lista vacía
        if not boarding_passes:
            flight_data = FlightDataResponse(
                flight_id=flight.flight_id,
                takeoff_date_time=flight.takeoff_date_time,
                takeoff_airport=flight.takeoff_airport,
                landing_date_time=flight.landing_date_time,
                landing_airport=flight.landing_airport,
                airplane_id=flight.airplane_id,
                passengers=[]
            )
            return FlightResponse(code=200, data=flight_data)
        
        # Convertir a formato de respuesta (snake_case a camelCase) - Base
        passengers_data = []
        for bp in boarding_passes:
            # Crear objeto combinando datos del pasajero y boarding pass
            passenger_data = PassengerResponse(
                passenger_id=bp.passenger.passenger_id,
                dni=bp.passenger.dni,
                name=bp.passenger.name,
                age=bp.passenger.age,
                country=bp.passenger.country,
                boarding_pass_id=bp.boarding_pass_id,
                purchase_id=bp.purchase_id,
                seat_type_id=bp.seat_type_id,
                seat_id=bp.seat_id
            )
            passengers_data.append(passenger_data)
        
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