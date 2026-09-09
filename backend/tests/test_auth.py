def test_register_and_login_flow(client):
    # Register new user
    register_res = client.post(
        "/api/auth/register",
        json={"email": "architect@example.com", "password": "SecurePassword123!"},
    )
    assert register_res.status_code == 200
    reg_data = register_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "architect@example.com"

    # Try duplicate registration
    dup_res = client.post(
        "/api/auth/register",
        json={"email": "architect@example.com", "password": "AnotherPassword123!"},
    )
    assert dup_res.status_code == 400

    # Login with valid credentials
    login_res = client.post(
        "/api/auth/login",
        json={"email": "architect@example.com", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # Access current user profile
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "architect@example.com"


def test_invalid_login(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "WrongPassword"},
    )
    assert res.status_code == 401
