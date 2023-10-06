import uuid


user_id = str(uuid.uuid4())


async def test_user_create(client, test_db):
    sample_payload = {
        "user_id": user_id,
        "user_email": "john@example.com",
        "user_firstname": "John",
        "user_lastname": "Wick",
        "user_hashed_password": "BabaYaga53"
    }
    response = await client.post("/user_create", json=sample_payload)
    assert response.status_code == 201
    assert response.json() == {
        "Status": "Success",
        "User": {
            "user_email": "john@example.com",
            "user_firstname": "John",
            "user_lastname": "Wick"
        },
    }


async def test_user_list(client, test_db):
    response = await client.get("/users")
    assert response.status_code == 200
    assert response.json() == {
        "Status": "Success",
        "User": {
            "user_email": "john@example.com",
            "user_firstname": "John",
            "user_lastname": "Wick",
            "user_hashed_password": "BabaYaga53"
        },
    }


async def test_get_user_by_id(client, test_db):
    response = await client.get(f"/user_get_by_id/{user_id}")
    assert response.status_code == 200
    assert response.json() == {
        "Status": "Success",
        "User": {
            "user_email": "john@example.com",
            "user_firstname": "John",
            "user_lastname": "Wick",
            "user_hashed_password": "BabaYaga53"
        },
    }


async def test_user_update(client, test_db):
    sample_payload = {
        "user_id": user_id,
        "user_email": "johnwick@example.com",
        "user_firstname": "John",
        "user_lastname": "Wick",
        "user_hashed_password": "BabaYaga53"
    }
    response = await client.patch(f"/api/users/{user_id}", json=sample_payload)
    assert response.status_code == 202
    assert response.json() == {
        "Status": "Success",
        "User": {
            "user_email": "johnwick@example.com",
            "user_firstname": "John",
            "user_lastname": "Wick",
            "user_hashed_password": "BabaYaga53"
        },
    }


async def test_user_delete(client, test_db):
    response = await client.delete(f"/user_delete/{user_id}")
    assert response.status_code == 200
    assert response.json() == {
        "Status": "Success",
        "Message": "User deleted successfully",
    }


async def test_get_user_not_found(client, test_db):
    user_id = "16303002-876a-4f39-ad16-e715f151bab3"
    response = await client.get(f"/user_get_by_id/{user_id}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No User with id: `16303002-876a-4f39-ad16-e715f151bab3` found"
    }
