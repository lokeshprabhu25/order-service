import os
from datetime import datetime, timezone
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Order Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

ORDERS = [
    {
        "id": 1001,
        "user_id": 1,
        "customer_name": "Rajesh Kumar",
        "product": "Laptop",
        "quantity": 1,
        "amount": 55000,
        "status": "CONFIRMED",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

class OrderRequest(BaseModel):
    user_id: int
    product: str
    quantity: int
    amount: float

@app.get("/")
def root():
    return {
        "service": "order-service",
        "status": "running",
        "dependency": USER_SERVICE_URL
    }

@app.get("/health")
def health():
    return {"status": "UP", "service": "order-service"}

@app.get("/dependency-check")
async def dependency_check():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{USER_SERVICE_URL}/health")
            response.raise_for_status()
        return {"order_service": "UP", "user_service": "UP"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"User Service unavailable: {exc}")

@app.post("/orders")
async def create_order(order: OrderRequest):
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    if order.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Service-to-service dependency:
    # Order Service validates customer using User Service.
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{USER_SERVICE_URL}/users/{order.user_id}")

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Customer does not exist")

            response.raise_for_status()
            customer = response.json()

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Cannot reach User Service: {exc}")

    new_id = max([o["id"] for o in ORDERS], default=1000) + 1

    new_order = {
        "id": new_id,
        "user_id": order.user_id,
        "customer_name": customer["name"],
        "product": order.product,
        "quantity": order.quantity,
        "amount": order.amount,
        "status": "CONFIRMED",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    ORDERS.append(new_order)

    return {
        "success": True,
        "message": "Order created successfully",
        "order": new_order
    }

@app.get("/orders")
def get_orders():
    return {"count": len(ORDERS), "orders": ORDERS}

@app.get("/orders/user/{user_id}")
def get_user_orders(user_id: int):
    user_orders = [o for o in ORDERS if o["user_id"] == user_id]
    return {"count": len(user_orders), "orders": user_orders}
