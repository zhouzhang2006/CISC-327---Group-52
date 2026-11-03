
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
