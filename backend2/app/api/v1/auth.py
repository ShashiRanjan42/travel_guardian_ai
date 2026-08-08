from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/login")
async def login(req: LoginRequest):
    # Hackathon simplified login
    if req.email == "meera@wayfare.in":
        role = "ops_agent"
    elif "rohan" in req.email:
        role = "traveller"
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return {
        "data": {
            "access_token": f"mock_jwt_{role}_{req.email}",
            "token_type": "bearer",
            "expires_in": 28800,
            "user": {
                "id": "usr_ops1" if role == "ops_agent" else "usr_trav1",
                "email": req.email,
                "full_name": "Meera Iyer" if role == "ops_agent" else "Rohan Desai",
                "role": role,
                "traveller_id": None if role == "ops_agent" else "trv_rohan_desai"
            }
        },
        "error": None,
        "meta": {}
    }

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    token = authorization.split(" ")[1]
    
    if "ops_agent" in token:
        return {"id": "usr_ops1", "email": "meera@wayfare.in", "full_name": "Meera Iyer", "role": "ops_agent", "traveller_id": None}
    elif "traveller" in token:
        email = token.split("_")[-1] if "_" in token else "rohan@example.com"
        # Mocking Rohan Desai
        return {"id": "usr_trav1", "email": email, "full_name": "Rohan Desai", "role": "traveller", "traveller_id": "trv_rohan_desai"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {"data": user}
