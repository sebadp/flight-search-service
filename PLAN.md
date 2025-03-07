# Implementación Paso a Paso

## Paso 1: Configuración del Proyecto

Inicializar un entorno virtual y definir las dependencias (FastAPI, Uvicorn, httpx, Pydantic, Pytest).

Estructurar el proyecto en módulos:
- `main.py` para la aplicación FastAPI.
- `models.py` para definir los modelos Pydantic.
- `services.py` o `logic.py` para la lógica de negocio que procesa los eventos de vuelo.
- `tests/` para los tests con Pytest.

## Paso 2: Definir Modelos con Pydantic

**Modelo de Evento de Vuelo:**
- Validar y convertir las fechas a objetos `datetime` para facilitar los cálculos.

**Modelo de Viaje:**
- Incluir los campos `connections` (cantidad de eventos) y `path` (lista de objetos de vuelo).

## Paso 3: Consumir la API Externa

- Crear un cliente (por ejemplo, usando `httpx`) que se encargue de hacer la llamada a `https://mock.apidog.com/m1/814105-793312-default/flight-events` para obtener los datos.
- Manejar errores en caso de que la API externa no esté disponible o retorne errores.

## Paso 4: Implementar la Lógica de Búsqueda

### Filtrado inicial:
- Filtrar los eventos de vuelo que operan en la fecha indicada.

### Búsqueda de vuelos directos:
- Seleccionar los eventos donde la ciudad de origen coincide con el parámetro `from` y la ciudad de destino con el parámetro `to`.
- Validar que la duración del vuelo (diferencia entre salida y llegada) no exceda 24 horas.

### Búsqueda de vuelos con conexión:
- Para cada vuelo que parte de la ciudad de origen, buscar un segundo vuelo cuya salida:
  - Sea desde la ciudad de llegada del primer vuelo.
  - Tenga un tiempo de espera menor o igual a 4 horas (la diferencia entre la llegada del primer vuelo y la salida del segundo).
  - Permita llegar a la ciudad de destino final.
- Verificar que la duración total del viaje (desde la salida del primer vuelo hasta la llegada del segundo) sea menor o igual a 24 horas.

## Paso 5: Exponer el Endpoint FastAPI

- Crear la ruta `GET /journeys/search` que reciba los parámetros.
- Invocar la función de búsqueda y retornar el JSON con el formato especificado.

## Paso 6: Pruebas Unitarias y de Integración con Pytest

Escribir pruebas para:
- Validar la correcta transformación y filtrado de datos.
- Casos de éxito para vuelos directos y con conexión.
- Manejo de escenarios donde no se encuentran vuelos válidos.
- Validación de errores en la entrada (por ejemplo, formato incorrecto de fecha o código de ciudad).

## Paso 7: Dockerización de la Aplicación

### Crear un `Dockerfile`:
- Seleccionar una imagen base (por ejemplo, `python:3.10-slim`).
- Instalar las dependencias.
- Copiar el código de la aplicación.
- Exponer el puerto y definir el comando de inicio (usando `Uvicorn`).

### (Opcional) `docker-compose`:
- Si se requiere levantar otros servicios o gestionar variables de entorno de manera más compleja.
