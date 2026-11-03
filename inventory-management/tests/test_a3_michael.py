
from unittest.mock import patch


# function to test that a low-stock notification is sent when a product's quantity_on_hand is at or below its reorder_level
def test_low_stock_notification_success(client):
    """test that a successful low-stock notification is reported"""

    # create test product with name, sku, unit_price, quantity_on_hand, and reorder_level
    product = {
        "name": "Test Product",
        "sku": "TEST-001",
        "unit_price": 10.0,
        "quantity_on_hand": 10,
        "reorder_level": 5,
    }

    product_resp = client.post("/products", json=product)
    assert product_resp.status_code == 201
    product_id = product_resp.get_json()["id"]

    movement = {
        "product_id": product_id,
        "quantity": 6,
        "type": "OUT",
    }

    with patch("app.routes.transactions.send_notification", return_value=True):
        response = client.post("/transactions", json=movement)

    assert response.status_code == 201
    assert response.get_json()["notification_sent"] is True

    # Verify that the inventory quantity was updated
    product_response = client.get(f"/products/{product_id}")
    assert product_response.get_json()["quantity_on_hand"] == 4


# function to test that the notification is sent with the correct arguments
def test_low_stock_notification_arguments(client):
    """Test that the notification is sent with the correct arguments."""

    product = {
        "name": "Test Product",
        "sku": "TEST-002",
        "unit_price": 10.0,
        "quantity_on_hand": 10,
        "reorder_level": 5,
    }

    product_resp = client.post("/products", json=product)
    assert product_resp.status_code == 201
    product_id = product_resp.get_json()["id"]

    movement = {
        "product_id": product_id,
        "quantity": 6,
        "type": "OUT",
    }

    # temporarily replaces the send_notification function with a mock that returns True and records calls
    with patch("app.routes.transactions.send_notification", return_value=True) as mock_send:
        response = client.post("/transactions", json=movement)

    assert response.status_code == 201
    assert response.get_json()["notification_sent"] is True

    mock_send.assert_called_once_with(
        "manager@example.com",
        "Low Stock Alert",
        "Product Test Product has only 4 units remaining."
    )

def test_update_missing_product(client):
    """Test updating a product that does not exist."""

    # attempt to update a product that does not exist
    response = client.put("/products/999", json={"name": "Updated Product"})

    # check that the response returns a 404 error
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


def test_stock_level_missing_product(client):
    """Test requesting stock level for a nonexistent product."""

    # attempt to retrieve the stock level of a product that does not exist
    response = client.get("/products/999/stock-level")

    # check that the response returns a 404 error
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


def test_product_supplier_missing_product(client):
    """Test retrieving a supplier for a nonexistent product."""

    # attempt to retrieve the supplier of a product that does not exist
    response = client.get("/products/999/supplier")

    # check that the response returns a 404 error
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


def test_product_supplier_unknown(client):
    """Test retrieving a supplier when the product has no supplier."""

    # create a product without assigning a supplier
    product = {
        "name": "Test Product",
        "sku": "TEST-003",
        "quantity_on_hand": 10,
        "reorder_level": 5
    }

    # send a request to create the product
    product_response = client.post("/products", json=product)
    assert product_response.status_code == 201

    # get the id of the newly created product
    product_id = product_response.get_json()["id"]

    # attempt to retrieve the supplier of the product
    response = client.get(f"/products/{product_id}/supplier")

    # check that the response returns a 404 error since no supplier exists
    assert response.status_code == 404
    assert response.get_json()["error"] == "Supplier unknown"


def test_update_product_invalid_supplier(client):
    """Test updating a product with a supplier that does not exist."""

    # create a product
    product = {
        "name": "Test Product",
        "sku": "TEST-004",
        "quantity_on_hand": 10,
        "reorder_level": 5
    }

    product_response = client.post("/products", json=product)
    assert product_response.status_code == 201
    product_id = product_response.get_json()["id"]

    # attempt to update the product with an invalid supplier
    response = client.put(
        f"/products/{product_id}",
        json={"supplier_id": 999}
    )

    # check that the response returns a 400 error
    assert response.status_code == 400
    assert response.get_json()["error"] == "Supplier not found"

def test_product_supplier_success(client):
    """Test retrieving the supplier of a product"""

    # create a supplier
    supplier = {
        "name": "Test Supplier",
        "contact_email": "supplier@example.com"
    }

    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 201
    supplier_id = supplier_response.get_json()["id"]

    # create a product linked to the supplier
    product = {
        "name": "Test Product",
        "sku": "TEST-005",
        "quantity_on_hand": 10,
        "reorder_level": 5,
        "supplier_id": supplier_id
    }

    product_response = client.post("/products", json=product)
    assert product_response.status_code == 201
    product_id = product_response.get_json()["id"]

    # retrieve the supplier associated with the product
    response = client.get(f"/products/{product_id}/supplier")

    # check that the correct supplier is returned
    assert response.status_code == 200
    assert response.get_json()["id"] == supplier_id
    assert response.get_json()["name"] == "Test Supplier"


def test_filter_transactions_by_product(client):
    """Test filtering transactions by product id."""

    # create two products
    product1 = {
        "name": "Product 1",
        "sku": "PROD-001",
        "quantity_on_hand": 10,
        "reorder_level": 5
    }

    product2 = {
        "name": "Product 2",
        "sku": "PROD-002",
        "quantity_on_hand": 10,
        "reorder_level": 5
    }

    response1 = client.post("/products", json=product1)
    response2 = client.post("/products", json=product2)

    assert response1.status_code == 201
    assert response2.status_code == 201

    product_id1 = response1.get_json()["id"]
    product_id2 = response2.get_json()["id"]

    # create a transaction for each product
    client.post("/transactions", json={
        "product_id": product_id1,
        "quantity": 2,
        "type": "IN"
    })

    client.post("/transactions", json={
        "product_id": product_id2,
        "quantity": 3,
        "type": "IN"
    })

    # retrieve transactions for the first product
    response = client.get(f"/transactions?product_id={product_id1}")

    # check that only the first product's transaction is returned
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0]["product_id"] == product_id1


def test_filter_transactions_by_supplier(client):
    """Test filtering transactions by supplier id."""

    # create two suppliers
    supplier1 = {
        "name": "Supplier 1",
        "contact_email": "supplier1@example.com"
    }

    supplier2 = {
        "name": "Supplier 2",
        "contact_email": "supplier2@example.com"
    }

    response1 = client.post("/suppliers", json=supplier1)
    response2 = client.post("/suppliers", json=supplier2)

    assert response1.status_code == 201
    assert response2.status_code == 201

    supplier_id1 = response1.get_json()["id"]
    supplier_id2 = response2.get_json()["id"]

    # create a product
    product = {
        "name": "Test Product",
        "sku": "PROD-003",
        "quantity_on_hand": 10,
        "reorder_level": 5
    }

    product_response = client.post("/products", json=product)
    assert product_response.status_code == 201
    product_id = product_response.get_json()["id"]

    # create a transaction for each supplier
    client.post("/transactions", json={
        "product_id": product_id,
        "supplier_id": supplier_id1,
        "quantity": 2,
        "type": "IN"
    })

    client.post("/transactions", json={
        "product_id": product_id,
        "supplier_id": supplier_id2,
        "quantity": 3,
        "type": "IN"
    })

    # retrieve transactions for the first supplier
    response = client.get(f"/transactions?supplier_id={supplier_id1}")

    # check that only the first supplier's transaction is returned
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0]["supplier_id"] == supplier_id1

def test_transaction_missing_product(client):
    """Test creating a transaction for a product that does not exist."""

    # attempt to create a transaction with an invalid product id
    movement = {
        "product_id": 999,
        "quantity": 5,
        "type": "IN"
    }

    response = client.post("/transactions", json=movement)

    # check that the response returns a 404 error
    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


def test_transaction_invalid_type(client):
    """Test creating a transaction with an invalid type."""

    # create a product
    product = {
        "name": "Test Product",
        "sku": "PROD-004",
        "quantity_on_hand": 10,
        "reorder_level": 5
    }

    product_response = client.post("/products", json=product)
    assert product_response.status_code == 201
    product_id = product_response.get_json()["id"]

    # attempt to create a transaction with an invalid type
    movement = {
        "product_id": product_id,
        "quantity": 5,
        "type": "INVALID"
    }

    response = client.post("/transactions", json=movement)

    # check that the response returns a 400 error
    assert response.status_code == 400
    assert response.get_json()["error"] == "type must be IN or OUT"

    # check that the product quantity remains unchanged
    product_response = client.get(f"/products/{product_id}")
    assert product_response.get_json()["quantity_on_hand"] == 10
