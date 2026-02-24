# FastAPI Microservices Architecture & API Gateway

This repository contains a fully functional microservices architecture built using Python and FastAPI. It demonstrates the API Gateway pattern by routing client requests to independent backend services while handling cross-cutting concerns like authentication and logging at the edge.

[cite_start]This project was developed for **Practical 3** [cite: 4] [cite_start]of the **IT4020 - Modern Topics in IT** [cite: 5] [cite_start]module at **SLIIT**[cite: 1].

## 🚀 Features

* [cite_start]**API Gateway Pattern:** A centralized entry point (Port 8000) that securely routes HTTP traffic to downstream microservices using `httpx`[cite: 10, 15].
* **Independent Microservices:** * **Student Service (Port 8001):** Manages student data with full CRUD capabilities.
  * **Course Service (Port 8002):** Manages course catalog data.
* **JWT Authentication:** Secures gateway endpoints using JSON Web Tokens (OAuth2), ensuring only authorized users can access the downstream services.
* **Observability (Logging Middleware):** Custom middleware intercepts all incoming requests to calculate processing times and log transaction details to the console.
* **Resilient Error Handling:** Enhanced exception handling to gracefully manage network timeouts (504) and offline services (503).

## 🛠️ Tech Stack

* [cite_start]**Python 3.8+** [cite: 12]
* [cite_start]**FastAPI:** High-performance web framework[cite: 13].
* [cite_start]**Uvicorn:** ASGI web server for running FastAPI[cite: 14].
* [cite_start]**HTTPx:** Async HTTP client for gateway routing[cite: 15].
* [cite_start]**Pydantic:** Data validation and settings management[cite: 15].
* **PyJWT:** JSON Web Token generation and validation.

## 📂 Project Structure

```text
microservices-fastapi/
│
├── gateway/
│   └── main.py              # API Gateway, Auth, and Logging Middleware
│
├── student-service/
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # Pydantic schemas
│   ├── service.py           # Business logic
│   └── data_service.py      # Mock database operations
│
├── course-service/
│   └── main.py              # Course API and models
│
└── requirements.txt         # Project dependencies
```

##⚙️ Installation & Setup

1. Clone the repository and navigate to the root directory:
```bash
git clone <your-repo-url>
cd microservices-fastapi
```
2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
## 🏃‍♂️ Running the Application

To experience the full architecture, you must run all three services simultaneously in separate terminal windows. Ensure your virtual environment is active in each terminal.

Terminal 1: Start the Student Service
```bash
cd student-service
uvicorn main:app --reload --port 8001
```
Terminal 2: Start the Course Service
```bash
cd course-service
uvicorn main:app --reload --port 8002
```
Terminal 3: Start the API Gateway
```bash
cd gateway
uvicorn main:app --reload --port 8000
```
## 🧪 Testing the API

Once all services are running, interact with the API Gateway via the automatic Swagger UI documentation:
  1. Open your browser and navigate to: http://localhost:8000/docs
  2. Click the green Authorize button at the top right.
  3. Log in using the test credentials:
       ```
       Username: admin
       Password: password
       ```
  4. You can now execute requests against the /gateway/students and /gateway/courses endpoints.
  5. Check Terminal 3 to see the logging middleware tracking your request times!

