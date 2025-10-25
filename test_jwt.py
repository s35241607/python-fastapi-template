import base64

from fastapi.testclient import TestClient

from app.main import app

# Create token like in conftest
header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
payload = base64.urlsafe_b64encode(b'{"sub":"1","type":"access"}').decode().rstrip("=")
signature = base64.urlsafe_b64encode(b"fake_signature").decode().rstrip("=")
token = f"{header}.{payload}.{signature}"

print("Token:", token)

client = TestClient(app)
response = client.get("/api/v1/test/jwt", headers={"Authorization": f"Bearer {token}"})
print("Status:", response.status_code)
print("Response:", response.json())
