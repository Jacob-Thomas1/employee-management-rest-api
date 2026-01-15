from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import Base, engine, SessionLocal
from .models import Employee
from .schemas import EmployeeCreate, EmployeeResponse
from .auth import create_access_token
from .dependencies import verify_token
from .crud import get_employee_by_email

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token")
def login():
    return {"access_token": create_access_token()}

@app.post("/api/employees/", response_model=EmployeeResponse, status_code=201, dependencies=[Depends(verify_token)])
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    if get_employee_by_email(db, emp.email):
        raise HTTPException(status_code=400, detail="Email exists")
    employee = Employee(**emp.dict())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@app.get("/api/employees/", response_model=List[EmployeeResponse], dependencies=[Depends(verify_token)])
def list_employees(department: str = None, role: str = None, page: int = 1, db: Session = Depends(get_db)):
    q = db.query(Employee)
    if department:
        q = q.filter(Employee.department == department)
    if role:
        q = q.filter(Employee.role == role)
    return q.offset((page-1)*10).limit(10).all()

@app.get("/api/employees/{id}", response_model=EmployeeResponse, dependencies=[Depends(verify_token)])
def get_employee(id: int, db: Session = Depends(get_db)):
    emp = db.get(Employee, id)
    if not emp:
        raise HTTPException(status_code=404)
    return emp

@app.put("/api/employees/{id}", response_model=EmployeeResponse, dependencies=[Depends(verify_token)])
def update_employee(id: int, emp: EmployeeCreate, db: Session = Depends(get_db)):
    employee = db.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404)
    for k, v in emp.dict().items():
        setattr(employee, k, v)
    db.commit()
    db.refresh(employee)
    return employee

@app.delete("/api/employees/{id}", status_code=204, dependencies=[Depends(verify_token)])
def delete_employee(id: int, db: Session = Depends(get_db)):
    employee = db.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404)
    db.delete(employee)
    db.commit()
