<<<<<<< HEAD
# flight-search-service
Repositorio de un servicio de búsqueda de vuelos con FastAPI. Consume una API externa para obtener eventos de vuelo y genera itinerarios de hasta dos vuelos, cumpliendo restricciones de 24h de viaje y 4h de conexión. Usa Pydantic, Pytest, httpx y Docker.
=======
# Servicio de Búsqueda de Vuelos

Este proyecto implementa la primera versión de un servicio de búsqueda de vuelos para una compañía aérea. El servicio permite obtener los viajes disponibles a partir de una lista de eventos de vuelo, filtrados por fecha, ciudad de origen y ciudad de destino.

## Descripción del Desafío

La compañía aérea cuenta con una API que provee la lista de **eventos de vuelo**. Cada evento de vuelo contiene:
- **Número de vuelo**
- **Fecha y hora de salida** (en UTC)
- **Fecha y hora de llegada** (en UTC)
- **Ciudad de origen**
- **Ciudad de destino**

Un **viaje** es una secuencia de uno o dos eventos de vuelo que conecta una ciudad de origen con una ciudad de destino, partiendo en una fecha determinada. Las restricciones para un viaje son:
- Máximo de 2 eventos de vuelo por viaje.
- La duración total del viaje (desde la salida del primer vuelo hasta la llegada del último) no debe exceder 24 horas.
- El tiempo de conexión (espera entre vuelos) no debe ser mayor a 4 horas.

El endpoint de búsqueda es un `GET` a la URL `/journeys/search` que recibe los siguientes parámetros:
- `date`: Fecha de salida en formato `YYYY-MM-DD`
- `from`: Código de ciudad de 3 letras (por ejemplo, "BUE")
- `to`: Código de ciudad de 3 letras (por ejemplo, "MAD")

La respuesta es un JSON con la siguiente estructura:

```json
[
  {
    "connections": 0,
    "path": [
      {
        "flight_number": "XX1234",
        "from": "BUE",
        "to": "MAD",
        "departure_time": "2024-09-12 00:00",
        "arrival_time": "2024-09-13 00:00"
      }
    ]
  }
]
Para obtener la lista de eventos de vuelo se utiliza un servicio mock en:
https://mock.apidog.com/m1/814105-793312-default/flight-events

Estructura del Proyecto
La estructura básica del proyecto es la siguiente:

bash
Copiar
├── main.py          # Archivo principal con la aplicación FastAPI
├── models.py        # Modelos Pydantic para eventos de vuelo y viajes
├── services.py      # Lógica de negocio para la búsqueda de vuelos
├── tests/           # Pruebas unitarias e integración (Pytest)
├── Dockerfile       # Archivo para dockerizar la aplicación
├── requirements.txt # Dependencias del proyecto
└── README.md        # Este archivo
Asunciones y Consideraciones
Manejo de horarios y zonas horarias:
Todos los cálculos y presentaciones se realizan en UTC.
Orden y presentación de resultados:
En caso de múltiples viajes válidos, se ordenan por la hora de salida del primer vuelo en orden ascendente.
Casos extremos y manejo de errores:
Si no se encuentran viajes, se retorna una lista vacía.
Se implementan validaciones para el formato de la fecha y los códigos de ciudad (deben tener 3 letras). En caso de error, se retorna un mensaje descriptivo (por ejemplo, error 422 de FastAPI).
Consumo del API externo:
Se realiza una consulta en tiempo real al servicio mock. Se implementa un mecanismo básico de reintentos en caso de error o falta de respuesta.
Instalación y Ejecución
Clonar el Repositorio
bash
Copiar
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
Crear y Activar el Entorno Virtual
bash
Copiar
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
Instalar Dependencias
bash
Copiar
pip install -r requirements.txt
Ejecutar la Aplicación
bash
Copiar
uvicorn main:app --reload
La aplicación estará disponible en: http://localhost:8000

Pruebas
Para ejecutar los tests unitarios y de integración:

bash
Copiar
pytest
Dockerización
Construir la Imagen Docker
bash
Copiar
docker build -t flight-search-service .
Ejecutar el Contenedor
bash
Copiar
docker run -p 8000:8000 flight-search-service
La aplicación estará disponible en: http://localhost:8000

Contribución
El proyecto se ha desarrollado siguiendo las mejores prácticas de la industria. Se agradecen contribuciones, sugerencias y mejoras.

>>>>>>> 05b3264 (Probando pre-commit con black)
