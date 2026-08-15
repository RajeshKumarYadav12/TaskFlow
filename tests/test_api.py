def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_signup(client, db_session):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login(client, db_session):
    # Setup user
    client.post(
        "/api/v1/auth/signup",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_project_crud(client, db_session):
    # Signup and login
    client.post("/api/v1/auth/signup", json={"email": "test2@example.com", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", data={"username": "test2@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Project
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"},
        headers=headers
    )
    assert response.status_code == 201
    project_id = response.json()["id"]
    
    # Get Projects
    response = client.get("/api/v1/projects/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    
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
    assert len(tasks_res.json()) == 1
    assert tasks_res.json()[0]["title"] == "Test Task"
