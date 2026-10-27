def test_update_product(client):
	"""Creates a product and tests if product updates can be successfully applied.
	Also tests to ensure updates for a non-existing product correctly return a 404.
	"""

	# Not Found edgecase
	not_found_resp = client.put("/products/0")
	assert not_found_resp.status_code == 404

	# Create the product
	product = {
		"name": "Original Product",
		"sku": "PROD-001",
		"unit_price": 9.99,
		"quantity_on_hand": 50,
		"reorder_level": 10,
	}
	create_resp = client.post("/products", json=product)
	assert create_resp.status_code == 201
	product_id = create_resp.get_json()["id"]

	# Update the product & verify response
	product["name"] = "Updated Product"
	product["quantity_on_hand"] = 45
	update_resp = client.put(f"/products/{product_id}", json=product)
	assert update_resp.status_code == 200
	assert update_resp.get_json() == product | {"id": product_id}

	# Verify update was properly saved
	get_resp = client.get(f"/products/{product_id}")
	assert get_resp.status_code == 200
	assert get_resp.get_json() == product | {"id": product_id}


def test_delete_product(client):
	"""Creates a product and tests to see if it gets deleted.
	Also tests for the application to gracefully handle an unknown product id with a 404.
	"""

	# Not Found edgecase
	not_found_resp = client.delete("/products/0")
	assert not_found_resp.status_code == 404

	# Create the product
	product = {
		"name": "Original Product",
		"sku": "PROD-001",
		"unit_price": 9.99,
		"quantity_on_hand": 50,
		"reorder_level": 10,
	}
	create_resp = client.post("/products", json=product)
	assert create_resp.status_code == 201
	product_id = create_resp.get_json()["id"]

	# Delete the product
	delete_resp = client.delete(f"/products/{product_id}")
	assert delete_resp.status_code == 204

	# Verify deletion
	get_resp = client.get(f"/products/{product_id}")
	assert get_resp.status_code == 404


def test_get_supplier(client):
	"""Creates a supplier and tests the retrieval of the supplier.
	Also tests for the application to gracefully handle an unknown supplier id with a 404.
	"""

	# Not Found edgecase
	not_found_resp = client.get("/suppliers/0")
	assert not_found_resp.status_code == 404

	# Create the supplier
	supplier = {"name": "Test Supplier", "contact_email": "supplier@example.com"}
	create_resp = client.post("/suppliers", json=supplier)
	assert create_resp.status_code == 201
	supplier_id = create_resp.get_json()["id"]

	# Test supplier can be retrieved
	get_resp = client.get(f"/suppliers/{supplier_id}")
	assert get_resp.status_code == 200
	assert get_resp.get_json() == (supplier | {"id": supplier_id})


def test_update_supplier(client):
	"""Creates a supplier and tests if supplier updates can be successfully applied.
	Also ensures updates for an unknown supplier id gracefully return a 404.
	"""

	# Not Found edgecase
	not_found_resp = client.put("/suppliers/0")
	assert not_found_resp.status_code == 404

	# Create the supplier
	supplier = {"name": "Test Supplier", "contact_email": "supplier@example.com"}
	create_resp = client.post("/suppliers", json=supplier)
	assert create_resp.status_code == 201
	supplier_id = create_resp.get_json()["id"]

	# Update the supplier & verify response
	supplier["name"] = "Updated Supplier"
	update_resp = client.put(f"/suppliers/{supplier_id}", json=supplier)
	assert update_resp.status_code == 200
	assert update_resp.get_json() == (supplier | {"id": supplier_id})

	# Verify update was properly saved
	get_resp = client.get(f"/suppliers/{supplier_id}")
	assert get_resp.status_code == 200
	assert get_resp.get_json() == (supplier | {"id": supplier_id})
