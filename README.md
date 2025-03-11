# Flight Search Service

A flight search service that finds direct and connecting flights based on user queries. Built using **FastAPI**, **Pydantic**, and **Pytest**.

---

## 🚀 Features

- Fetches real-time flight data from an external API
- Supports searching for **direct flights** and **one-stop connections**
- Implements **FastAPI** for a high-performance backend
- Uses **Redis caching** to improve performance and reduce API calls
- Validates search parameters using **Pydantic models**
- Includes **unit and integration tests** with `pytest`
- Automated CI/CD pipeline using **GitHub Actions**
- Pre-commit hooks using **black** for code formatting
- **Dockerized** and includes **Docker Compose** for easy deployment

---

## 🛆 Installation

### **1. Clone the repository**

```bash
git clone git@github.com:sebadp/flight-search-service.git
cd flight-search-service
```

### **2. Create a virtual environment & install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

pip install -r requirements.txt
```

### **3. Create and Configure .env File**

This service uses environment variables stored in a `.env` file.

Copy the example file:

```bash
cp .env.example .env
```

Open `.env` and configure the variables:

```ini
API_URL=https://mock.apidog.com/m1/814105-793312-default/flight-events
REDIS_HOST=redis
REDIS_URL=redis://redis:6379
MAX_RETRIES=3
TIMEOUT=5.0
```

---

## 🚀 Running the Service

### **Option 1: Running Locally**

Start the FastAPI server manually:

```bash
uvicorn main:app --reload
```

🚨 **Note:** Redis must be running for caching to work. You can start a Redis container with:

```bash
docker run --name redis -d -p 6379:6379 redis
```

### **🐋 Option 2: Running with Docker Compose**

To run the service along with Redis in a containerized environment:

```bash
docker-compose up --build
```

🚀 This will:

- Start the FastAPI app on http://localhost:8000
- Start a Redis container for caching

To stop the service:

```bash
docker-compose down
```

---

## 🐜 API Documentation

Once the server is running, you can access:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🛠 Running Tests

To run all unit and integration tests:

```bash
pytest
```

If you’re using Docker Compose, run tests inside the container:

```bash
docker exec -it fastapi_app pytest
```

---

## 🐋 Running with Docker (Standalone)

If you want to run the service without Docker Compose, build and run manually:

```bash
docker build -t flight-search-service .
docker run --env-file .env -p 8000:8000 flight-search-service
```

---

## 🚀 Continuous Integration with GitHub Actions

This project uses **GitHub Actions** to run tests on each push or pull request to `main` or `develop`.

---

## 🐜 API Endpoint

### **Search for flights**

#### **GET /journeys/search**

**Query Parameters:**

- `date` (YYYY-MM-DD) – Travel date
- `from` (IATA Code) – Departure city
- `to` (IATA Code) – Arrival city

#### **Example Request:**

```bash
curl "http://127.0.0.1:8000/journeys/search?date=2024-09-12&origin=BUE&destination=MAD"
```

#### **Example Response:**

```json
[
    {
        "connections": 0,
        "path": [
            {
                "flight_number": "XX1234",
                "from": "BUE",
                "to": "MAD",
                "departure_time": "2024-09-12 12:00:00",
                "arrival_time": "2024-09-13 00:00:00"
            }
        ]
    }
]
```

---

## 📝 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Sebastián Dávila**

Feel free to contribute, open issues, or suggest improvements! 🚀

