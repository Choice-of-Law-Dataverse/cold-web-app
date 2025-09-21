from fastapi.testclient import TestClient

from app.auth import verify_jwt_token

# Import your FastAPI app and the dependency to override
from app.main import app


# Create an override function that simulates successful JWT verification.
def override_verify_jwt_token():
    # This can return a dummy payload if your endpoints rely on it,
    # or simply not raise an error.
    return {"sub": "test_user"}


# Apply the dependency override.
app.dependency_overrides[verify_jwt_token] = override_verify_jwt_token

# Initialize the TestClient with the FastAPI app.
client = TestClient(app)


def test_root():
    # Make a GET request to the root endpoint.
    response = client.get("/")

    # Assert that the request was successful.
    assert response.status_code == 200

    # Assert that the JSON response is as expected.
    assert response.json() == {"message": "Hello World from CoLD"}
