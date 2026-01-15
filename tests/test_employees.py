import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Test fixtures
@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def get_valid_token():
    """Helper to get a valid JWT token"""
    response = client.post("/token")
    return response.json()["access_token"]

# ==================== AUTHENTICATION TESTS ====================

def test_get_token():
    """Test POST /token endpoint returns access token"""
    response = client.post("/token")
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["access_token"] is not None

# ==================== CREATE EMPLOYEE TESTS ====================

def test_create_employee_success():
    """Test creating employee with valid data"""
    token = get_valid_token()
    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Software Engineer"
    }
    response = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["id"] is not None

def test_create_employee_duplicate_email():
    """Test creating employee with duplicate email fails"""
    token = get_valid_token()
    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Software Engineer"
    }
    
    # Create first employee
    response1 = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 400
    assert "Email exists" in response2.json()["detail"]

def test_create_employee_without_auth():
    """Test creating employee without token fails"""
    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Software Engineer"
    }
    response = client.post("/api/employees/", json=employee_data)
    assert response.status_code == 401

def test_create_employee_invalid_email():
    """Test creating employee with invalid email format"""
    token = get_valid_token()
    employee_data = {
        "name": "John Doe",
        "email": "not-an-email",
        "department": "Engineering",
        "role": "Developer"
    }
    response = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422  # Validation error

# ==================== LIST EMPLOYEES TESTS ====================

def test_list_employees_empty():
    """Test listing employees when database is empty"""
    token = get_valid_token()
    response = client.get(
        "/api/employees/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []

def test_list_employees_success():
    """Test listing employees returns all employees"""
    token = get_valid_token()
    
    # Create multiple employees
    for i in range(3):
        employee_data = {
            "name": f"Employee {i}",
            "email": f"employee{i}@example.com",
            "department": "Engineering",
            "role": "Developer"
        }
        client.post(
            "/api/employees/",
            json=employee_data,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    response = client.get(
        "/api/employees/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_list_employees_filter_by_department():
    """Test filtering employees by department"""
    token = get_valid_token()
    
    # Create employees in different departments
    departments = [
        {"name": "Alice", "email": "alice@example.com", "department": "Engineering", "role": "Dev"},
        {"name": "Bob", "email": "bob@example.com", "department": "HR", "role": "Manager"},
        {"name": "Charlie", "email": "charlie@example.com", "department": "Engineering", "role": "Dev"},
    ]
    
    for emp in departments:
        client.post(
            "/api/employees/",
            json=emp,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Filter by Engineering
    response = client.get(
        "/api/employees/?department=Engineering",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    for emp in response.json():
        assert emp["department"] == "Engineering"

def test_list_employees_filter_by_role():
    """Test filtering employees by role"""
    token = get_valid_token()
    
    # Create employees with different roles
    roles = [
        {"name": "Alice", "email": "alice@example.com", "department": "Engineering", "role": "Senior Dev"},
        {"name": "Bob", "email": "bob@example.com", "department": "Engineering", "role": "Junior Dev"},
        {"name": "Charlie", "email": "charlie@example.com", "department": "Engineering", "role": "Senior Dev"},
    ]
    
    for emp in roles:
        client.post(
            "/api/employees/",
            json=emp,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Filter by Senior Dev
    response = client.get(
        "/api/employees/?role=Senior Dev",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    for emp in response.json():
        assert emp["role"] == "Senior Dev"

def test_list_employees_pagination():
    """Test pagination with page parameter"""
    token = get_valid_token()
    
    # Create 15 employees (more than one page)
    for i in range(15):
        employee_data = {
            "name": f"Employee {i:02d}",
            "email": f"emp{i:02d}@example.com",
            "department": "Engineering",
            "role": "Developer"
        }
        client.post(
            "/api/employees/",
            json=employee_data,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Get page 1
    response1 = client.get(
        "/api/employees/?page=1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 200
    assert len(response1.json()) == 10
    
    # Get page 2
    response2 = client.get(
        "/api/employees/?page=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200
    assert len(response2.json()) == 5

def test_list_employees_without_auth():
    """Test listing employees without token fails"""
    response = client.get("/api/employees/")
    assert response.status_code == 401

# ==================== GET EMPLOYEE BY ID TESTS ====================

def test_get_employee_by_id_success():
    """Test getting employee by valid ID"""
    token = get_valid_token()
    
    # Create an employee
    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Software Engineer",
        "salary": 75000
    }
    create_response = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    emp_id = create_response.json()["id"]
    
    # Get the employee
    response = client.get(
        f"/api/employees/{emp_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == emp_id
    assert response.json()["name"] == "John Doe"

def test_get_employee_not_found():
    """Test getting employee with non-existent ID"""
    token = get_valid_token()
    response = client.get(
        "/api/employees/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_get_employee_without_auth():
    """Test getting employee without token fails"""
    response = client.get("/api/employees/1")
    assert response.status_code == 401

# ==================== UPDATE EMPLOYEE TESTS ====================

def test_update_employee_success():
    """Test updating employee with valid data"""
    token = get_valid_token()
    
    # Create an employee
    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Software Engineer"
    }
    create_response = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    emp_id = create_response.json()["id"]
    
    # Update the employee
    updated_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "department": "Management",
        "role": "Team Lead"
    }
    response = client.put(
        f"/api/employees/{emp_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"
    assert response.json()["role"] == "Team Lead"

def test_update_employee_not_found():
    """Test updating non-existent employee"""
    token = get_valid_token()
    updated_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "department": "Management",
        "role": "Team Lead",
        "salary": 95000
    }
    response = client.put(
        "/api/employees/999",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_update_employee_partial():
    """Test partial update of employee"""
    token = get_valid_token()
    
    # Create an employee
    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Software Engineer"
    }
    create_response = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    emp_id = create_response.json()["id"]
    
    # Update role
    updated_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Senior Software Engineer"
    }
    response = client.put(
        f"/api/employees/{emp_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "Senior Software Engineer"
    assert response.json()["name"] == "John Doe"

def test_update_employee_without_auth():
    """Test updating employee without token fails"""
    updated_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "department": "Management",
        "role": "Team Lead"
    }
    response = client.put("/api/employees/1", json=updated_data)
    assert response.status_code == 401

# ==================== DELETE EMPLOYEE TESTS ====================

def test_delete_employee_success():
    """Test deleting employee"""
    token = get_valid_token()
    
    # Create an employee
    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Software Engineer",
        "salary": 75000
    }
    create_response = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    emp_id = create_response.json()["id"]
    
    # Delete the employee
    response = client.delete(
        f"/api/employees/{emp_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204
    
    # Verify employee is deleted
    get_response = client.get(
        f"/api/employees/{emp_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404

def test_delete_employee_not_found():
    """Test deleting non-existent employee"""
    token = get_valid_token()
    response = client.delete(
        "/api/employees/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_delete_employee_without_auth():
    """Test deleting employee without token fails"""
    response = client.delete("/api/employees/1")
    assert response.status_code == 401

# ==================== INTEGRATION TESTS ====================

def test_full_crud_workflow():
    """Test complete CRUD workflow"""
    token = get_valid_token()
    
    # Create
    employee_data = {
        "name": "Test Employee",
        "email": "test@example.com",
        "department": "Testing",
        "role": "QA Engineer"
    }
    create_response = client.post(
        "/api/employees/",
        json=employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    emp_id = create_response.json()["id"]
    
    # Read
    get_response = client.get(
        f"/api/employees/{emp_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 200
    
    # Update
    updated_data = {
        "name": "Updated Employee",
        "email": "updated@example.com",
        "department": "Testing",
        "role": "Senior QA Engineer"
    }
    update_response = client.put(
        f"/api/employees/{emp_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200
    
    # Delete
    delete_response = client.delete(
        f"/api/employees/{emp_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204
