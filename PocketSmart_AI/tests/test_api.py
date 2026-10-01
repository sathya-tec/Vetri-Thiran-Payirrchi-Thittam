import os


# Test configuration
os.environ["DATABASE_URL"] = (
    "sqlite:///./test_pocketsmart.db"
)

os.environ["SECRET_KEY"] = (
    "test-secret-key"
)

os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_register_login_and_home():

    email = (
        "test_pocketsmart@example.com"
    )

    register_response = client.post(
        "/api/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "password123",
        },
    )

    assert register_response.status_code in (
        201,
        409,
    )

    login_response = client.post(
        "/api/login",
        json={
            "email": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    home_response = client.post(
        "/api/generate-home",
        json={
            "budget": 50000,
            "rooms": [
                "Living Room"
            ],
            "style": "modern",
            "notes": "",
        },
    )

    assert home_response.status_code == 200

    data = home_response.json()

    assert "recommendations" in data
    assert "allocations" in data


def test_protected_history_requires_login():

    # Create a fresh client without
    # authentication cookies.
    fresh_client = TestClient(app)

    response = fresh_client.get(
        "/api/history"
    )

    assert response.status_code == 401