# Employee Management REST API

## Project Overview
The Employee Management REST API is a backend application built using **Python and FastAPI**.  
This project is designed to manage employee records within an organization by providing standard **CRUD (Create, Read, Update, Delete)** operations.

The API follows proper **RESTful design principles** and is secured using **token-based authentication**.  
As required in the assignment, all API endpoints were tested exclusively using **Postman**.

---

## Features
- Token-based authentication using JWT
- Full Create, Read, Update, and Delete operations for employees
- Email uniqueness validation to prevent duplicate records
- Pagination support for handling large datasets
- Filtering employees by department and role
- Proper usage of HTTP status codes
- Complete API testing using Postman

---

## Tech Stack
- **Language:** Python  
- **Framework:** FastAPI  
- **Database:** SQLite  
- **ORM:** SQLAlchemy  
- **Authentication:** JWT  
- **Testing Tool:** Postman  
- **Server:** Uvicorn  

---

## Project Structure
```text
employee-management-rest-api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── crud.py
│   └── dependencies.py
│
├── tests/
│   └── test_employees.py
│
├── requirements.txt
└── README.md
```


---

## How to Run the Project (Local Setup)
uvicorn app.main:app --reload