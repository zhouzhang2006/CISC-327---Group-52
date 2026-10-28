# enhancement R13: prevent incorrect inventory quantities

# test that a valid quantity is accepted
def test_valid_product_quantity(client):

    response = client.post("/products", json={
        "name": "Test Hammer",
        "sku": "HAMMER-01",
        "quantity_on_hand": 10
    })

    assert response.status_code == 201
    assert response.get_json()["quantity_on_hand"] == 10


# test that a negative quantity is rejected
def test_negative_product_quantity(client):

    response = client.post("/products", json={
        "name": "Test Hammer",
        "sku": "HAMMER-01",
        "quantity_on_hand": -5
    })

    assert response.status_code == 400
    assert response.get_json()["error"] == "Quantity must be a non-negative integer"


# test that text cannot be entered as a quantity
def test_invalid_product_quantity(client):

    response = client.post("/products", json={
        "name": "Test Hammer",
        "sku": "HAMMER-01",
        "quantity_on_hand": "abc"
    })

    assert response.status_code == 400
    assert response.get_json()["error"] == "Quantity must be a non-negative integer"