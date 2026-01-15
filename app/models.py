from sqlalchemy import Column, Integer, String, Date
from datetime import date
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String)
    role = Column(String)
    date_joined = Column(Date, default=date.today)
