from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class Airplane(Base):
    __tablename__ = "airplane"
    
    airplane_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    
    flight = relationship("Flight", back_populates="airplane")
    seat = relationship("Seat", back_populates="airplane")


class BoardingPass(Base):
    __tablename__ = "boarding_pass"
    
    boarding_pass_id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchase.purchase_id"))
    passenger_id = Column(Integer, ForeignKey("passenger.passenger_id"))
    seat_type_id = Column(Integer, ForeignKey("seat_type.seat_type_id"))
    seat_id = Column(Integer, ForeignKey("seat.seat_id"), nullable=True)
    flight_id = Column(Integer, ForeignKey("flight.flight_id"))
    
    purchase = relationship("Purchase", back_populates="boarding_pass")
    passenger = relationship("Passenger", back_populates="boarding_pass")
    seat_type = relationship("SeatType", back_populates="boarding_pass")
    seat = relationship("Seat", back_populates="boarding_pass")
    flight = relationship("Flight", back_populates="boarding_pass")


class Flight(Base):
    __tablename__ = "flight"
    
    flight_id = Column(Integer, primary_key=True, index=True)
    takeoff_date_time = Column(Integer)  # Unix timestamp
    takeoff_airport = Column(String(255))
    landing_date_time = Column(Integer)  # Unix timestamp
    landing_airport = Column(String(255))
    airplane_id = Column(Integer, ForeignKey("airplane.airplane_id"))
    
    airplane = relationship("Airplane", back_populates="flight")
    boarding_pass = relationship("BoardingPass", back_populates="flight")


class Passenger(Base):
    __tablename__ = "passenger"
    
    passenger_id = Column(Integer, primary_key=True, index=True)
    dni = Column(Integer)
    name = Column(String(255))
    age = Column(Integer)
    country = Column(String(255))
    
    boarding_pass = relationship("BoardingPass", back_populates="passenger")


class Purchase(Base):
    __tablename__ = "purchase"
    
    purchase_id = Column(Integer, primary_key=True, index=True)
    purchase_date = Column(DateTime)
    
    boarding_pass = relationship("BoardingPass", back_populates="purchase")


class Seat(Base):
    __tablename__ = "seat"
    
    seat_id = Column(Integer, primary_key=True, index=True)
    seat_column = Column(String(1))
    seat_row = Column(Integer)
    seat_type_id = Column(Integer, ForeignKey("seat_type.seat_type_id"))
    airplane_id = Column(Integer, ForeignKey("airplane.airplane_id"))
    
    airplane = relationship("Airplane", back_populates="seat")
    seat_type = relationship("SeatType", back_populates="seat")
    boarding_pass = relationship("BoardingPass", back_populates="seat")


class SeatType(Base):
    __tablename__ = "seat_type"
    
    seat_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))  # "Primera clase", "Clase económica premium", "Clase económica".
    
    seat = relationship("Seat", back_populates="seat_type")
    boarding_pass = relationship("BoardingPass", back_populates="seat_type")