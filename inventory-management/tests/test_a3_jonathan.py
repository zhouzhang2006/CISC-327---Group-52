from datetime import date

from app.models.purchase_order import PurchaseOrder


def test_list_empty_purchase_orders(client):
	"""Test listing zero purchase orders"""

	res = client.get("/purchase-orders")
	assert res.status_code == 200
	assert res.get_json() == []


def test_create_purchase_order(client):
	"""Tests creating purchase orders and listing them back out.
	Also, tests edgecases for missing products/suppliers.
	"""

	# Create supplier and product for po
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
	supplier = {"name": "Test Supplier", "contact_email": "supplier@example.com"}
	create_resp = client.post("/suppliers", json=supplier)
	assert create_resp.status_code == 201
	supplier_id = create_resp.get_json()["id"]

	missing_sup = client.post(
		"/purchase-orders", json={"supplier_id": 0, "product_id": product_id}
	)
	assert missing_sup.status_code == 404
	missing_prod = client.post(
		"/purchase-orders", json={"supplier_id": supplier_id, "product_id": 0}
	)
	assert missing_prod.status_code == 404

	# Test the full creation
	po = {"supplier_id": supplier_id, "product_id": product_id, "quantity_ordered": 100}
	res = client.post("/purchase-orders", json=po)
	assert res.status_code == 201
	res_json = res.get_json()
	assert res_json["supplier_id"] == supplier_id
	assert res_json["product_id"] == product_id
	assert res_json["quantity_ordered"] == 100
	assert res_json["status"] == "pending"
	assert res_json["created_date"] == str(date.today())
	assert res_json["received_date"] is None

	# List it back out to ensure it saved
	res = client.get("/purchase-orders")
	assert res.status_code == 200
	assert res.get_json() == [res_json]


def test_get_purchase_order(client):
	"""Tests retrieving a purchase order that was created. Also tests missing purchase order."""

	missing_res = client.get("/purchase-orders/0")
	assert missing_res.status_code == 404

	# Create purchase order
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
	supplier = {"name": "Test Supplier", "contact_email": "supplier@example.com"}
	create_resp = client.post("/suppliers", json=supplier)
	assert create_resp.status_code == 201
	supplier_id = create_resp.get_json()["id"]
	po = {"supplier_id": supplier_id, "product_id": product_id, "quantity_ordered": 100}
	po_res = client.post("/purchase-orders", json=po)
	assert po_res.status_code == 201

	# Test get
	res = client.get(f"/purchase-orders/{po_res.get_json()['id']}")
	assert res.status_code == 200
	assert res.get_json() == po_res.get_json()


def test_receive_purchase_order(client):
	"""Tests receiving a purchase order that was created. Also tests missing/received purchase order."""

	missing_res = client.put("/purchase-orders/0/receive")
	assert missing_res.status_code == 404

	# Create purchase order
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
	supplier = {"name": "Test Supplier", "contact_email": "supplier@example.com"}
	create_resp = client.post("/suppliers", json=supplier)
	assert create_resp.status_code == 201
	supplier_id = create_resp.get_json()["id"]
	po = {"supplier_id": supplier_id, "product_id": product_id, "quantity_ordered": 100}
	po_res = client.post("/purchase-orders", json=po)
	po_id = po_res.get_json()["id"]
	assert po_res.status_code == 201

	# Test receive
	res = client.put(f"/purchase-orders/{po_id}/receive")
	assert res.status_code == 200
	res_json = res.get_json()
	assert res_json["id"] == po_id
	assert res_json["status"] == "received"
	assert res_json["received_date"] == str(date.today())
	# Check transaction was created
	trans_res = client.get("/transactions")
	assert trans_res.status_code == 200
	transaction_count = len(trans_res.get_json())
	latest_transaction = trans_res.get_json()[-1]
	assert latest_transaction["product_id"] == product_id
	assert latest_transaction["supplier_id"] == supplier_id
	assert latest_transaction["quantity"] == 100

	# Test second receive
	res = client.put(f"/purchase-orders/{po_id}/receive")
	assert res.status_code == 400
	trans_res = client.get("/transactions")
	assert trans_res.status_code == 200
	assert transaction_count == len(trans_res.get_json())


def test_purchase_order_model():
	"""ensures the po model gets created correctly"""
	po = PurchaseOrder(
		id=1,
		supplier_id=2,
		product_id=3,
		quantity_ordered=100,
		status="pending",
	)
	assert po.id == 1
	assert po.supplier_id == 2
	assert po.product_id == 3
	assert po.quantity_ordered == 100
	assert po.status == "pending"
	assert po.created_date == date.today()
	assert po.received_date == None


def test_supplier_products(client):
	"""Tests to ensure products received from a given supplier are returned.
	Also tests to ensure unknown supplier ids are correctly rejected.
	"""
	# Test 404
	res = client.get("suppliers/0/products")
	assert res.status_code == 404

	# Create products and suppliers
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
	product2 = {
		"name": "Another Product",
		"sku": "PROD-002",
		"unit_price": 5.99,
		"quantity_on_hand": 10,
		"reorder_level": 5,
	}
	create_resp = client.post("/products", json=product2)
	assert create_resp.status_code == 201
	product2_id = create_resp.get_json()["id"]
	product3 = {
		"name": "Other Product",
		"sku": "PROD-003",
		"unit_price": 5.99,
		"quantity_on_hand": 10,
		"reorder_level": 5,
	}
	create_resp = client.post("/products", json=product3)
	assert create_resp.status_code == 201
	supplier = {"name": "Test Supplier", "contact_email": "supplier@example.com"}
	create_resp = client.post("/suppliers", json=supplier)
	assert create_resp.status_code == 201
	supplier_id = create_resp.get_json()["id"]

	# test the route, expect nothing
	res = client.get(f"/suppliers/{supplier_id}/products")
	assert res.status_code == 200
	assert res.get_json() == []

	# Create a few transactions
	trans_1 = {
		"product_id": product_id,
		"supplier_id": supplier_id,
		"quantity": 10,
		"type": "IN",
	}
	in_resp = client.post("/transactions", json=trans_1)
	assert in_resp.status_code == 201
	trans_1["id"] = in_resp.get_json()["id"]

	trans_2 = {
		"product_id": product2_id,
		"supplier_id": supplier_id,
		"quantity": 5,
		"type": "IN",
	}
	out_resp = client.post("/transactions", json=trans_2)
	assert out_resp.status_code == 201
	trans_2["id"] = out_resp.get_json()["id"]

	# test the route
	res = client.get(f"/suppliers/{supplier_id}/products")
	assert res.status_code == 200
	json = res.get_json()
	assert len(json) == 2
	assert json[0]["id"] in [product_id, product2_id]
	assert json[1]["id"] in [product_id, product2_id]


def test_ui_post_transaction(client):
	"""Tests the UI route for posting a transaction."""
	# Create product and supplier
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

	tx = {
		"product_id": product_id,
		"type": "OUT",
		"quantity": 5,
	}
	create_resp = client.post("/ui/transactions", data=tx)
	assert create_resp.status_code == 302

	# Ensure the transaction was saved
	res_transactions = client.get("/transactions")
	assert res_transactions.status_code == 200
	transactions = res_transactions.get_json()
	assert len(transactions) == 1
	assert transactions[0]["product_id"] == product_id
	assert transactions[0]["type"] == "OUT"
	assert transactions[0]["quantity"] == 5
