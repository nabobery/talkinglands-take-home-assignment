def test_generate_map_image(client):
    params = {"bbox": "0,0,10,10"}  # Example bounding box coordinates
    response = client.get("/images/generate-map-image", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "image_url" in data
    assert data["image_url"].startswith("http")