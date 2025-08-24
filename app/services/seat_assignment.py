from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.models import BoardingPass, Seat
from collections import defaultdict

class SeatAssignmentService:
    def __init__(self, db: Session):
        self.db = db
        # Configuración de aviones
        self.airplane_configs = {
            1: {'sections': [['A', 'B', 'C'], ['E', 'F', 'G']], 'adjacent': [('A','B'), ('B','C'), ('E','F'), ('F','G')]},
            2: {'sections': [['A', 'B'], ['D', 'E', 'F'], ['H', 'I']], 'adjacent': [('A','B'), ('D','E'), ('E','F'), ('H','I')]}
        }
    

    def assign_seats_for_flight(self, flight_id: int) -> List[BoardingPass]:        
        boarding_passes = self.db.query(BoardingPass).filter(
            BoardingPass.flight_id == flight_id
        ).options(joinedload(BoardingPass.passenger), joinedload(BoardingPass.flight)).all()
        
        if not boarding_passes:
            return []
        
        airplane_id = boarding_passes[0].flight.airplane_id
        available_seats = self._get_available_seats(airplane_id, flight_id)
        purchase_groups = self._group_by_purchase(boarding_passes)
        
        self._assign_individuals(purchase_groups, available_seats)
        

        return boarding_passes
    

    def _group_by_purchase(self, boarding_passes: List[BoardingPass]) -> Dict[int, List[BoardingPass]]:
        """Agrupa por purchase_id."""
        groups = defaultdict(list)
        for bp in boarding_passes:
            groups[bp.purchase_id].append(bp)
        return dict(groups)
    

    def _get_available_seats(self, airplane_id: int, flight_id: int) -> Dict[int, List[Seat]]:
        """Obtiene asientos disponibles por tipo."""
        # Consulta única con LEFT JOIN para obtener asientos disponibles
        available_seats = self.db.query(Seat).outerjoin(
            BoardingPass, 
            (BoardingPass.seat_id == Seat.seat_id) & (BoardingPass.flight_id == flight_id)
        ).filter(
            Seat.airplane_id == airplane_id,
            BoardingPass.seat_id.is_(None)
        ).order_by(Seat.seat_row, Seat.seat_column).all()
        
        seats_by_type = defaultdict(list)
        for seat in available_seats:
            seats_by_type[seat.seat_type_id].append(seat)
        
        return dict(seats_by_type)
    
    
    def _assign_individuals(self, purchase_groups: Dict[int, List[BoardingPass]], 
                          available_seats: Dict[int, List[Seat]]) -> None:
        """Asigna asientos a todos los pasajeros sin asiento."""
        for group in purchase_groups.values():
            for bp in group:
                if not bp.seat_id:  # Cualquier pasajero sin asiento
                    seat = self._get_next_seat(bp.seat_type_id, available_seats)
                    if seat:
                        bp.seat_id = seat.seat_id
                        available_seats[seat.seat_type_id].remove(seat)
    
    
    def _get_next_seat(self, seat_type_id: int, available_seats: Dict[int, List[Seat]]) -> Optional[Seat]:
        """Obtiene siguiente asiento disponible."""
        if seat_type_id in available_seats and available_seats[seat_type_id]:
            return available_seats[seat_type_id][0]
        return None