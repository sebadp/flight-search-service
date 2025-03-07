# Flight Search Service

&#x20;

A flight search service that finds direct and connecting flights based on user queries. Built using **FastAPI**, **Pydantic**, and **Pytest**.

---

## 🚀 Features

- Fetches real-time flight data from an external API
- Supports searching for **direct flights** and **one-stop connections**
- Validates search parameters using **Pydantic models**
- Implements **FastAPI** for a high-performance backend
- Includes **unit and integration tests** with `pytest`
- Automated CI/CD pipeline using **GitHub Actions**
- Pre-commit hooks using **black** for code formatting
- **Dockerized** for easy deployment

---

## 📦 Installation

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

### **3. Install pre-commit hooks (optional but recommended)**

```bash
pre-commit install
```

This ensures that `black` runs before every commit to enforce code formatting.

---

## 🚀 Running the Service

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

### **API Documentation**

Once the server is running, you can access:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🛠 Running Tests

To run all unit and integration tests:

```bash
pytest
```

---

## 🐳 Running with Docker

To run the service inside a Docker container:

```bash
docker build -t flight-search-service .
docker run -p 8000:8000 flight-search-service
```

---

## 🚀 Continuous Integration with GitHub Actions

This project uses **GitHub Actions** to run tests on each `push` or `pull request` to `main` or `develop`. You can check the status of the latest builds in the **Actions** tab of your repository.

---

## 📜 API Endpoint

### **Search for flights**

`GET /journeys/search`

**Query Parameters:**

- `date` (YYYY-MM-DD) – Travel date
- `origin` (IATA Code) – Departure city
- `destination` (IATA Code) – Arrival city

**Example Request:**

```bash
curl "http://127.0.0.1:8000/journeys/search?date=2024-09-12&origin=BUE&destination=MAD"
```

**Example Response:**

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

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Sebastián** - Developer of Flight Search Service.

Feel free to contribute, open issues, or suggest improvements! 🚀

