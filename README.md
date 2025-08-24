# RETO BSALE - DESARROLLADOR WEB JUNIOR 2025

API para simulación de check-in de vuelos con asignación automática de asientos.

## 📋 Descripción

Esta API simula el proceso de check-in de vuelos, asignando automáticamente asientos a los pasajeros siguiendo reglas de negocio específicas para optimizar la experiencia de viaje de grupos y familias.

## 🏗️ Arquitectura

### Orden de Asignación de Asientos

1. **🧒 Grupos con menores de edad** - Prioridad máxima
   - Asientos adulto-menor adyacentes
   - Grupos más grandes primero

2. **🔗 Grupos con asientos pre-asignados** - Segunda prioridad
   - Junta miembros restantes cerca de asientos ya asignados
   - Cálculo de distancia optimizado

3. **👥 Grupos grandes restantes** - Tercera prioridad
   - Asientos consecutivos en la misma sección
   - Ordenados por tamaño descendente

4. **👤 Pasajeros individuales** - Última prioridad
   - Cualquier pasajero sin asiento asignado
   - Asientos disponibles restantes

### Tipos de Avión Soportados

**Avión Tipo 1 (ABC EFG):**
```
Fila 1:  [A] [B] [C]    [E] [F] [G]
Fila 2:  [A] [B] [C]    [E] [F] [G]
```

**Avión Tipo 2 (AB DEF HI):**
```
Fila 1:  [A] [B]   [D] [E] [F]   [H] [I]
Fila 2:  [A] [B]   [D] [E] [F]   [H] [I]
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.10
- MySQL 8.0+
- pip (gestor de paquetes de Python)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Jeremymr2/bsale-challenge-2025.git
cd bsale-challenge-2025
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

Crear archivo `.env` en la raíz del proyecto:

```env
DB_HOST=tu-host-mysql
DB_USER=tu-usuario
DB_PASSWORD=tu-contraseña
DB_NAME=db-name
```

## 🏃‍♂️ Ejecución

### Desarrollo

```bash
# Opción 1: Usando el script run.py
python run.py

# Opción 2: Usando uvicorn directamente
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación de la API

### Endpoints Principales

#### 🏠 Health Check
```http
GET /
GET /health
```

#### ✈️ Vuelos
```http
GET /flights/{flight_id}/passengers
```

### Documentación Interactiva

Una vez que la API esté ejecutándose, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Ejemplo de Uso

```bash
# Obtener pasajeros de un vuelo con asientos asignados
curl -X GET "http://localhost:8000/flights/1/passengers"
```

**Respuesta esperada:**
```json
{
  "code": 200,
  "data": {
    "flightId": 1,
    "takeoffDateTime": "2024-12-25T10:30:00",
    "takeoffAirport": "SCL",
    "landingDateTime": "2024-12-25T14:45:00",
    "landingAirport": "LIM",
    "airplaneId": 1,
    "passengers": [
      {
        "passengerId": 1,
        "dni": "12345678",
        "name": "Juan Pérez",
        "age": 35,
        "country": "Chile",
        "boardingPassId": 1,
        "purchaseId": 1,
        "seatTypeId": 1,
        "seatId": 15
      }
    ]
  }
}
```

## 🗄️ Estructura de Base de Datos

### Tablas Principales

- **flights**: Información de vuelos
- **passengers**: Datos de pasajeros
- **boarding_passes**: Tarjetas de embarque
- **seats**: Asientos del avión
- **seat_types**: Tipos de asiento (económico, business, etc.)
- **purchases**: Compras agrupadas

## 🔧 Desarrollo

### Estructura del Proyecto

```
bsale-challenge-2025/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── database.py          # Configuración de base de datos
│   ├── models/
│   │   └── models.py        # Modelos SQLAlchemy
│   ├── routers/
│   │   └── flights.py       # Endpoints de vuelos
│   ├── schemas/
│   │   └── auto_camel_schemas.py  # Esquemas Pydantic
│   └── services/
│       └── seat_assignment.py    # Lógica de asignación de asientos
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias
├── run.py                  # Script de ejecución
└── README.md               # Este archivo
```