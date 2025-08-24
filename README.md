# RETO BSALE - DESARROLLADOR WEB JUNIOR 2025

API para simulación de check-in de vuelos con asignación automática de asientos.

## Descripción

Esta API simula el proceso de check-in de vuelos, asignando automáticamente asientos a los pasajeros siguiendo reglas de negocio específicas para optimizar la experiencia de viaje de grupos y familias.

## Arquitectura

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

## Instalación y Configuración

### Prerrequisitos

- Python 3.9.23
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

## Ejecución

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

## Documentación de la API

### Endpoints Principales

#### Health Check
```http
GET /
GET /health
```

#### Vuelos
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
    "takeoffDateTime": 1688207580,
    "takeoffAirport": "Aeropuerto Internacional Arturo Merino Benitez, Chile",
    "landingDateTime": 1688221980,
    "landingAirport": "Aeropuerto Internacional Jorge Cháve, Perú",
    "airplaneId": 1,
    "passengers": [
      {
        "passengerId": 515,
        "dni": 41771513,
        "name": "Camila",
        "age": 80,
        "country": "Chile",
        "boardingPassId": 1,
        "purchaseId": 69,
        "seatTypeId": 2,
        "seatId": 87
      },
...
    ]
  }
}
```

## Estructura de Base de Datos

### Tablas Principales

- **airplane**: Información del avión
- **boarding_pass**: Tarjetas de embarque
- **flight**: Información de vuelos
- **passenger**: Datos de pasajeros
- **purchase**: Compras agrupadas
- **seat**: Asientos del avión
- **seat_type**: Tipos de asiento (económico, business, etc.)

## Desarrollo

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
│   ├── services/
│   │   └── seat_assignment.py    # Lógica de asignación de asientos
│   └── utils/
│       └── case_converter.py    # Función que transforma de snake_case a camelCase
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias
├── run.py                  # Script de ejecución
└── README.md               # Este archivo
```


## Lógica Detallada de Asignación de Asientos

### Algoritmo Principal

El sistema implementa un algoritmo de asignación inteligente que procesa a los pasajeros en **4 fases secuenciales**, cada una con reglas específicas para optimizar la experiencia de viaje.

### Fase 1: Grupos con Menores de Edad (Prioridad Máxima)

**Objetivo**: Garantizar que los menores de edad (< 18 años) siempre estén sentados junto a un adulto.

**Proceso**:
1. **Identificación**: Detecta todos los grupos (mismo `purchase_id`) que contengan al menos un menor de edad
2. **Ordenamiento**: Ordena por tamaño de grupo (más grandes primero) para maximizar opciones
3. **Estrategia de Asignación**:
   - **Pares Adulto-Menor Adyacentes**: Busca asientos estrictamente adyacentes (misma fila, columnas pegadas)
   - **Agrupación por Tipo**: Procesa por separado cada tipo de asiento (económico, business, etc.)
   - **Patrón Alternado**: Asigna en secuencia adulto-menor-adulto-menor cuando es posible

**Ejemplo**:
```
Familia: Juan (35), María (32), Sofía (8) - purchase_id: 1
Resultado: [1A-Juan] [1B-Sofía] [1C-María]
```

**Reglas de Adyacencia**:
- **Avión Tipo 1**: A-B, B-C, E-F, F-G son adyacentes
- **Avión Tipo 2**: A-B, D-E, E-F, H-I son adyacentes
- **No adyacentes**: C-E (separados por pasillo)

### Fase 2: Grupos con Asientos Pre-asignados (Segunda Prioridad)

**Objetivo**: Reunir a los miembros restantes de grupos que ya tienen algunos asientos asignados.

**Proceso**:
1. **Filtrado**: Identifica grupos de 2+ personas sin menores que tengan asientos parcialmente asignados
2. **Ordenamiento**: Prioriza grupos con menos personas sin asignar (mejor oportunidad de éxito)
3. **Cálculo de Distancia**: Usa algoritmo de distancia optimizado para encontrar asientos cercanos

**Algoritmo de Distancia**:
```python
distancia = diferencia_filas + (diferencia_columnas * 0.5)
```
- **Prioriza misma fila**: Diferencia de columnas tiene menor peso
- **Ejemplo**: Asiento 1A vs 1C = 0 + (2 * 0.5) = 1.0
- **Ejemplo**: Asiento 1A vs 2A = 1 + (0 * 0.5) = 1.0

**Ejemplo**:
```
Grupo: Carlos (28), Ana (26) - purchase_id: 2
Carlos ya asignado en 2E
Resultado: Ana asignada en 2F (adyacente) o 2D (cercano)
```

### Fase 3: Grupos Grandes Restantes (Tercera Prioridad)

**Objetivo**: Asignar grupos completos sin asientos en bloques consecutivos.

**Proceso**:
1. **Filtrado**: Solo grupos de 2+ personas completamente sin asignar y sin menores
2. **Ordenamiento**: Grupos más grandes primero (mejor aprovechamiento de bloques)
3. **Búsqueda de Consecutivos**: Encuentra asientos en la misma sección del avión

**Definición de Consecutivos**:
- **Misma fila**: Todos los asientos en la misma fila
- **Misma sección**: Dentro del mismo bloque (ABC o EFG en Tipo 1)
- **Ordenados**: Secuencia natural de columnas (A, B, C)

**Ejemplo**:
```
Grupo de 3: Pedro, Luis, Carmen - purchase_id: 3
Resultado: [3A-Pedro] [3B-Luis] [3C-Carmen] (consecutivos en sección ABC)
```

**Secciones por Avión**:
- **Tipo 1**: Sección ABC (ventana-medio-pasillo), Sección EFG (pasillo-medio-ventana)
- **Tipo 2**: Sección AB (ventana-pasillo), Sección DEF (pasillo-medio-pasillo), Sección HI (pasillo-ventana)

### Fase 4: Pasajeros Restantes (Última Prioridad)

**Objetivo**: Asignar cualquier pasajero que no haya recibido asiento en las fases anteriores.

**Proceso**:
1. **Sin filtros**: Procesa cualquier pasajero sin asiento, independiente del tamaño de grupo
2. **Asignación simple**: Primer asiento disponible de su tipo
3. **Red de seguridad**: Garantiza que nadie se quede sin asiento

**Casos cubiertos**:
- Personas que viajan solas
- Miembros de grupos grandes que no pudieron sentarse juntos
- Pasajeros de grupos con menores donde no todos cupieron cerca
- Cualquier caso edge no cubierto por fases anteriores
