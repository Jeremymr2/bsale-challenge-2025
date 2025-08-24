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
        
        print ("Asignando asientos para grupos con menores de edad")
        self._assign_groups_with_minors(purchase_groups, available_seats, airplane_id)
        print ("Asignando asientos para el resto de los pasajeros")
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

    ### FUNCIONES AUXILIARES ###
    def _assign_minor_adult_pairs(self, minors: List[BoardingPass], adults: List[BoardingPass],
                                 seat_type_id: int, available_seats: Dict[int, List[Seat]], airplane_id: int) -> None:
        """Asigna pares adulto-menor adyacentes."""
        if seat_type_id not in available_seats:
            return
        # Asignar pares adyacentes
        for i in range(min(len(minors), len(adults))):
            pair = self._find_adjacent_pair(seat_type_id, available_seats, airplane_id)
            if pair:
                adults[i].seat_id = pair[0].seat_id
                minors[i].seat_id = pair[1].seat_id
                available_seats[seat_type_id].remove(pair[0])
                available_seats[seat_type_id].remove(pair[1])
        # Asignar restantes
        for bp in minors + adults:
            if not bp.seat_id:
                seat = self._get_next_seat(seat_type_id, available_seats)
                if seat:
                    bp.seat_id = seat.seat_id
                    available_seats[seat_type_id].remove(seat)

    
    def _find_adjacent_pair(self, seat_type_id: int, available_seats: Dict[int, List[Seat]], 
                           airplane_id: int) -> Optional[Tuple[Seat, Seat]]:
        """Encuentra par de asientos adyacentes."""
        if seat_type_id not in available_seats:
            return None
        
        seats = available_seats[seat_type_id]
        config = self.airplane_configs.get(airplane_id, self.airplane_configs[1])
        adjacent_set = set(config['adjacent'])  # Convertir a set para búsqueda O(1)
        
        # Agrupar por fila para búsqueda más eficiente
        by_row = defaultdict(list)
        for seat in seats:
            by_row[seat.seat_row].append(seat)
        
        # Buscar en cada fila
        for row_seats in by_row.values():
            if len(row_seats) < 2:
                continue
            for i, seat1 in enumerate(row_seats):
                for seat2 in row_seats[i+1:]:
                    if ((seat1.seat_column, seat2.seat_column) in adjacent_set or
                        (seat2.seat_column, seat1.seat_column) in adjacent_set):
                        return (seat1, seat2)
        return None


    def _get_next_seat(self, seat_type_id: int, available_seats: Dict[int, List[Seat]]) -> Optional[Seat]:
        """Obtiene siguiente asiento disponible."""
        if seat_type_id in available_seats and available_seats[seat_type_id]:
            return available_seats[seat_type_id][0]
        return None


    ### FUNCIONES PARA ASIGNACIÓN DE ASIENTOS ###

    def _assign_groups_with_minors(self, purchase_groups: Dict[int, List[BoardingPass]], 
                                  available_seats: Dict[int, List[Seat]], airplane_id: int) -> None:
        """Asigna grupos con menores, priorizando adulto-menor adyacente."""
        groups_with_minors = [(group) for group in purchase_groups.values() 
                             if any(bp.passenger.age < 18 for bp in group)]
        
        groups_with_minors.sort(key=len, reverse=True)
        
        for group in groups_with_minors:
            unassigned = [bp for bp in group if not bp.seat_id]
            if not unassigned:
                continue
                
            minors = [bp for bp in unassigned if bp.passenger.age < 18]
            adults = [bp for bp in unassigned if bp.passenger.age >= 18]
            
            by_type = defaultdict(lambda: {'minors': [], 'adults': []})
            for bp in minors:
                by_type[bp.seat_type_id]['minors'].append(bp)
            for bp in adults:
                by_type[bp.seat_type_id]['adults'].append(bp)
            
            for seat_type_id, passengers in by_type.items():
                self._assign_minor_adult_pairs(passengers['minors'], passengers['adults'], 
                                             seat_type_id, available_seats, airplane_id)
    
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