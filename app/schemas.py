from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: Optional[str] = None
    role: Optional[str] = None

class EmployeeResponse(EmployeeCreate):
    id: int
    date_joined: date

    class Config:
        orm_mode = True
