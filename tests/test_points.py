def test_create_point(client):
    payload = {
        "name": "Test Point",
        "latitude": 12.34,
        "longitude": 56.78,
        "meta": {"info": "test"}
    }
    response = client.post("/points/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Point"

def test_get_points(client):
    response = client.get("/points/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)