def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    data = response.json()

    assert "status_code" in data
    assert "detail" in data
    assert "result" in data
