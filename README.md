# Employee Management REST API
🚀
📌 Overview
The Employee Management REST API is a backend application built with Python and FastAPI.
It provides a robust system to manage employee records through standard CRUD (Create, Read, Update, Delete) operations, while adhering to RESTful best practices.
Authentication is handled via JWT tokens, ensuring secure access to protected endpoints.
All endpoints have been thoroughly tested using Postman.

✨ Features
- 🔐 JWT Authentication for secure access
- 📄 Complete CRUD operations for employee records
- 📧 Email uniqueness validation to avoid duplicates
- 📊 Pagination for large datasets
- 🔎 Filtering by department and role
- ✅ Proper usage of HTTP status codes
- 🧪 Comprehensive Postman testing

🛠 Tech Stack
- Language: Python
- Framework: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Authentication: JWT
- Testing Tool: Postman
- Server: Uvicorn
📂 Project Structure
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



▶️ Running the Project Locally


Start the development server with:

uvicorn app.main:app --reload


The API will be available at:
👉 http://127.0.0.1:8000

