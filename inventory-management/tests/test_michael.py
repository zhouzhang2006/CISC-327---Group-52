# Michael's tests for features 1, 2, 5, 6, 7, and 8 for the inventory management system

# feature 1: list all products
def test_list_products(client):

    # add a product so we have something to look for
    client.post("/products", json={
        "name": "Test Hammer",
        "sku": "HAMMER-01",
        "unit_price": 15.99,
        "quantity_on_hand": 10
    })

    # get all of the products
    response = client.get("/products")

    assert response.status_code == 200

    products = response.get_json()

    # ensure the response gives us a list
    assert isinstance(products, list)

    # make sure our product appears in the list
    assert len(products) == 1
    assert products[0]["name"] == "Test Hammer"
    assert products[0]["sku"] == "HAMMER-01"
    assert products[0]["quantity_on_hand"] == 10


# feature 2: create a new product
def test_create_product(client):

    # create a new product
    product = {
        "name": "Test Hammer",
        "sku": "TEST-HAMMER",
        "unit_price": 15.99,
        "quantity_on_hand": 10,
        "reorder_level": 2
    }

    response = client.post("/products", json=product)
    assert response.status_code == 201
    created_product = response.get_json()

    # make sure the product was created with the information we provided
    assert created_product["name"] == "Test Hammer"
    assert created_product["sku"] == "TEST-HAMMER"
    assert created_product["unit_price"] == 15.99
    assert created_product["quantity_on_hand"] == 10
    assert created_product["reorder_level"] == 2
    assert "id" in created_product

    # check that the product can be found after creating it
    product_id = created_product["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    found_product = response.get_json()
    assert found_product["id"] == product_id
    assert found_product["name"] == "Test Hammer"


# feature 5: get one product
def test_get_one_product(client):

    # create a product so we know which product we want to look up
    product = {
        "name": "Test Drill",
        "sku": "TEST-DRILL",
        "unit_price": 25.00,
        "quantity_on_hand": 5
    }

    response = client.post("/products", json=product)
    assert response.status_code == 201
    product_id = response.get_json()["id"]

    # get the product using its ID
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    found_product = response.get_json()

    # make sure the returned product is the one we created
    assert found_product["id"] == product_id
    assert found_product["name"] == "Test Drill"
    assert found_product["sku"] == "TEST-DRILL"
    assert found_product["quantity_on_hand"] == 5


# feature 6: current product quantity on hand
def test_product_stock_level(client):

    # create a product with a known quantity
    product = {
        "name": "Test Saw",
        "sku": "TEST-SAW",
        "unit_price": 20.00,
        "quantity_on_hand": 15
    }

    response = client.post("/products", json=product)

    assert response.status_code == 201

    product_id = response.get_json()["id"]

    # check the current stock level for the product
    response = client.get(f"/products/{product_id}/stock-level")

    assert response.status_code == 200

    stock_level = response.get_json()

    # the stock level should match the quantity entered
    assert stock_level["product_id"] == product_id
    assert stock_level["quantity_on_hand"] == 15


# feature 7: list all the suppliers
def test_list_suppliers(client):

    # add a supplier so we have something to look for
    client.post("/suppliers", json={
        "name": "Test Supplier",
        "contact_email": "test@supplier.com"
    })

    # get all of the suppliers
    response = client.get("/suppliers")

    assert response.status_code == 200

    suppliers = response.get_json()

    # make sure the response gives us a list
    assert isinstance(suppliers, list)

    # make sure our supplier appears in the list
    assert len(suppliers) == 1
    assert suppliers[0]["name"] == "Test Supplier"
    assert suppliers[0]["contact_email"] == "test@supplier.com"


# feature 8: create a supplier
def test_create_supplier(client):

    # create a new supplier
    supplier = {
        "name": "Test Supplier",
        "contact_email": "test@supplier.com"
    }

    response = client.post("/suppliers", json=supplier)

    assert response.status_code == 201

    created_supplier = response.get_json()

    # ensure that the supplier was created correctly
    assert created_supplier["name"] == "Test Supplier"
    assert created_supplier["contact_email"] == "test@supplier.com"
    assert "id" in created_supplier

    # check that the supplier can be found after creating it
    supplier_id = created_supplier["id"]

    response = client.get(f"/suppliers/{supplier_id}")

    assert response.status_code == 200

    found_supplier = response.get_json()

    assert found_supplier["id"] == supplier_id
    assert found_supplier["name"] == "Test Supplier"
    assert found_supplier["contact_email"] == "test@supplier.com"

# extra test - get a product that does not exist
def test_get_missing_product(client):

    # try to get a product with an ID that does not exist
    response = client.get("/products/999")

    assert response.status_code == 404

    # make sure the response explains the error
    assert response.get_json()["error"] == "Product not found"

# extra test #2 - get a supplier that does not exist
def test_get_missing_supplier(client):

    # try to get a supplier with an ID that does not exist
    response = client.get("/suppliers/999")

    assert response.status_code == 404

    # make sure the response explains the error
    assert response.get_json()["error"] == "Supplier not found"