def test_create_polygon(client):
    payload = {
        "name": "Test Polygon",
        "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]],
        "metadata": {"color": "blue"}
    }
    response = client.post("/polygons/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Polygon"
    assert "image_url" in data

def test_get_polygons(client):
    response = client.get("/polygons/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)