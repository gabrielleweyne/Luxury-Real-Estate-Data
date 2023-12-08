from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
test_user = {"email": "teste@teste.com", "password": 123}
estate_keys = [
    "address",
    "dorms",
    "lat",
    "lng",
    "parking",
    "price",
    "toilets",
    "source",
    "source_id",
    "timestamp",
    "total_area",
    "estate_ind_id",
    "img"
]


def validate_estates_format(estates_json):
    for e in estates_json:
        for k in dict.keys(e):
            if k not in estate_keys:
                return False
    return True


def test_estates():
    resp = client.post("/api/users/login", params=test_user)
    assert resp.status_code == 201

    resp = client.get("/api/estates")
    assert resp.status_code == 200
    assert validate_estates_format(resp.json())
