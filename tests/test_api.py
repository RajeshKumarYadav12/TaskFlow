def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_signup(client, db_session):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "signup_test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["status"] == "success"
    data = json_data["data"]
    assert data["email"] == "signup_test@example.com"
    assert "id" in data

def test_login(client, db_session):
    # Setup user
    client.post(
        "/api/v1/auth/signup",
        json={"email": "login_test@example.com", "password": "password123"}
    )
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "access_token" in json_data["data"]

def test_project_crud(client, db_session):
    # Signup and login
    client.post("/api/v1/auth/signup", json={"email": "crud_test@example.com", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", json={"email": "crud_test@example.com", "password": "password123"})
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Project
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"},
        headers=headers
    )
    assert response.status_code == 201
    project_id = response.json()["data"]["id"]
    
    # Get Projects
    response = client.get("/api/v1/projects/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    
    # Create Task
    task_res = client.post(
        "/api/v1/tasks/",
        json={"title": "Test Task", "project_id": project_id},
        headers=headers
    )
    assert task_res.status_code == 201
    
    # Get Tasks
    tasks_res = client.get("/api/v1/tasks/", headers=headers)
    assert tasks_res.status_code == 200
    assert len(tasks_res.json()["data"]) == 1
    assert tasks_res.json()["data"][0]["title"] == "Test Task"
