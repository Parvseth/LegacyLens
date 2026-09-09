import io
import zipfile


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_project_lifecycle(client):
    # Register and get auth token
    reg_res = client.post(
        "/api/auth/register",
        json={"email": "tester@example.com", "password": "Password123!"},
    )
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create dummy in-memory zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("main.py", "import os\n\ndef run():\n    print('Hello LegacyLens')\n")
    zip_buffer.seek(0)

    # Upload ZIP
    upload_res = client.post(
        "/api/projects/upload",
        files={"file": ("test_project.zip", zip_buffer, "application/zip")},
        data={"name": "Test Project"},
        headers=headers,
    )
    assert upload_res.status_code == 200
    proj = upload_res.json()
    project_id = proj["id"]
    assert proj["name"] == "Test Project"

    # List projects
    list_res = client.get("/api/projects", headers=headers)
    assert list_res.status_code == 200
    assert any(p["id"] == project_id for p in list_res.json()["projects"])

    # Get single project
    get_res = client.get(f"/api/projects/{project_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == project_id

    # Delete project
    del_res = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify deleted
    get_after_del = client.get(f"/api/projects/{project_id}", headers=headers)
    assert get_after_del.status_code == 404
