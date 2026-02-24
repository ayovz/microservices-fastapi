# gateway/main.py
import time
import logging
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
import jwt
from typing import Any
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API_Gateway")

app = FastAPI(title="API Gateway", version="1.0.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 1. Note the exact time the request arrived
    start_time = time.time()
    
    # 2. Log what the user is asking for
    logger.info(f"Incoming: {request.method} {request.url}")
    
    # 3. Pass the request down to the actual route (like /gateway/students)
    response = await call_next(request)
    
    # 4. Calculate how long it took the microservice to respond
    process_time = time.time() - start_time
    
    # 5. Log the final result and the time it took
    logger.info(f"Completed: {response.status_code} | Took: {process_time:.4f}s")
    
    return response

# --- Auth Setup ---
SECRET_KEY = "my_super_secret_lab_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Hardcoded dummy user for the lab exercise
    if form_data.username != "admin" or form_data.password != "password":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Generate a token valid for 30 minutes
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"sub": form_data.username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}

async def verify_token(token: str = Depends(oauth2_scheme)):
    """Dependency to check if the token is valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Service URLs
SERVICES = {
    "student": "http://localhost:8001",
    "course": "http://localhost:8002"
}

async def forward_request(service: str, path: str, method: str, **kwargs) -> Any:
    """Forward request to the appropriate microservice"""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    url = f"{SERVICES[service]}{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return JSONResponse(
                content=response.json() if response.text else None,
                status_code=response.status_code
            )
        except httpx.ConnectError:
            # Triggers if the microservice is completely turned off or unreachable
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail=f"The '{service}' microservice is currently offline or unreachable. Please try again later."
            )
        except httpx.TimeoutException:
            # Triggers if the microservice is running, but taking too long to answer
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT, 
                detail=f"The '{service}' microservice took too long to respond."
            )
        except httpx.RequestError as e:
            # A catch-all for any other network-level errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"An unexpected network error occurred communicating with the '{service}' service: {str(e)}"
            )

@app.get("/")
def read_root():
    return {"message": "API Gateway is running", "available_services": list(SERVICES.keys())}

# Student Service Routes
@app.get("/gateway/students")
async def get_all_students():
    """Get all students through gateway"""
    return await forward_request("student", "/api/students", "GET")

@app.get("/gateway/students/{student_id}")
async def get_student(student_id: int):
    """Get a student by ID through gateway"""
    return await forward_request("student", f"/api/students/{student_id}", "GET")

@app.post("/gateway/students")
async def create_student(request: Request):
    """Create a new student through gateway"""
    body = await request.json()
    return await forward_request("student", "/api/students", "POST", json=body)

@app.put("/gateway/students/{student_id}")
async def update_student(student_id: int, request: Request):
    """Update a student through gateway"""
    body = await request.json()
    return await forward_request("student", f"/api/students/{student_id}", "PUT", json=body)

@app.delete("/gateway/students/{student_id}")
async def delete_student(student_id: int):
    """Delete a student through gateway"""
    return await forward_request("student", f"/api/students/{student_id}", "DELETE")

# --- Course Service Routes ---

@app.get("/gateway/students")
async def get_all_students(user: dict = Depends(verify_token)): 
    """Get all students through gateway"""
    return await forward_request("student", "/api/students", "GET")

@app.post("/gateway/courses")
async def create_course(request: Request):
    """Create a new course through gateway"""
    body = await request.json()
    return await forward_request("course", "/api/courses", "POST", json=body)