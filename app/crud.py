from sqlalchemy.orm import Session
from .models import Employee

def get_employee_by_email(db: Session, email: str):
    return db.query(Employee).filter(Employee.email == email).first()
