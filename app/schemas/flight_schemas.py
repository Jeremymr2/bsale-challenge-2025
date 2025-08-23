from pydantic import BaseModel, Field
from typing import List, Optional
from app.utils.case_converter import snake_to_camel


class CamelCaseModel(BaseModel):
    """Modelo base que convierte automáticamente snake_case a camelCase."""
    
    class Config:
        alias_generator = snake_to_camel
        populate_by_name = True
        from_attributes = True


class PassengerResponse(CamelCaseModel):
    passenger_id: int
    dni: int
    name: str
    age: int
    country: str
    boarding_pass_id: int
    purchase_id: int
    seat_type_id: int
    seat_id: Optional[int] = None


class FlightDataResponse(CamelCaseModel):
    flight_id: int
    takeoff_date_time: int
    takeoff_airport: str
    landing_date_time: int
    landing_airport: str
    airplane_id: int
    passengers: List[PassengerResponse]


class FlightResponse(BaseModel):
    code: int
    data: FlightDataResponse


class FlightNotFoundResponse(BaseModel):
    code: int = 404
    errors: str = "flight not found"


class FlightErrorResponse(BaseModel):
    code: int = 400
    errors: str