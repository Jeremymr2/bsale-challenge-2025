# Notas

## Notas
Con esto, deberás crear una API REST con un solo endpoint que permita **consultar** por el **ID del vuelo** y **retornar la simulación**. Tal como muestra el ERD, una compra puede tener muchas tarjetas de embarque asociadas, pero estas tarjetas pueden no tener un asiento asociado, siempre tendrá un tipo de asiento, por lo tanto, al retornar la simulación del check-in se debe asignar el asiento a cada tarjeta de embarque. Los puntos a tomar en cuenta son:
- Todo pasajero menor de edad debe quedar al lado de al menos uno de sus acompañantes mayores de edad (se puede agrupar por el id de la compra).
- Si una compra tiene, por ejemplo, 4 tarjetas de embarque, tratar en lo posible que los asientos que se asignen estén juntos, o queden muy cercanos (ya sea en la fila o en la columna).
- Si una tarjeta de embarque pertenece a la clase “económica”, no se puede asignar un asiento de otra clase.


## Importante
- Los campos en la bd están llamados en Snake case, pero en la respuesta de la API deben ser transformados a Camel case.
- Se debe entregar la misma estructura de respuestas pues la API será testeada de forma automática, y si no cumple con la estructura el ejercicio quedará descartado.
- Contemplar buenas prácticas de programación, una manera de medir esto es pensando que estás desarrollando una aplicación que será utilizada en productivo.
- Utilizar control de versiones.
- Este ejercicio no tiene ningún fin comercial ni estratégico, sólo queremos medir tus habilidades y conocimientos.

## Extra
**¿Qué significa que todo pasajero menor de edad debe quedar “al lado” de al menos uno de sus acompañantes mayores de edad?**
- En palabras simples, por ejemplo, si el avión utilizado es el número 2, sirve que el menor de edad y su acompañante queden en los asientos A20 y B20. No es válido si quedan en los asientos B20 y D20. Debe ser el mismo número de filas pero con columnas pegadas, A con B, D con E, etc.



## Endpoint único


### GET /flights/:id/passengers
Respuesta exitosa
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
        "passengerId": 90,
        "dni": 983834822,
        "name": "Marisol",
        "age": 44,
        "country": "México",
        "boardingPassId": 24,
        "purchaseId": 47,
        "seatTypeId": 1,
        "seatId": 1
        },
        {...}
    ]
}
}
```

Vuelo no encontrado
```json
{
    "code": 404,
    "data": {}
}
```

En caso de error
```json
{
    "code": 400,
    "errors": "could not connect to db"
}
```


## Entregable

- Archivo README.md que indique como ejecutar la API y explicación de la solución. Agregar documentación del proyecto que consideres relevante.
- Código fuente en repositorio privado de GitHub, y acceso al usuario `postulaciones-bsale`
- Enviar mediante este formulario la siguiente información:  
-> CV en formato PDF.  
-> URL donde estará desplegada la API (AWS, GCP, DigitalOcean u otro servicio de hosting a tu elección).  
-> URL del repositorio de GitHub.  