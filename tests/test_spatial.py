def test_invalid_polygon_for_spatial_query(client):
    # Attempt to query points within a non-existent polygon.
    response = client.get("/spatial/points-in-polygon/9999")
    # Depending on implementation, this may return a 404 or an empty list.
    assert response.status_code in (200, 404)