from flask import Blueprint, jsonify, request

# we have to import the send_notification function from the notification_service module
from notification_service import send_notification
from app import store
from app.models.transaction import Transaction

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")


@transactions_bp.route("", methods=["GET"])
def list_transactions():
    results = list(store.transactions.values())
    product_id = request.args.get("product_id", type=int)
    supplier_id = request.args.get("supplier_id", type=int)
    if product_id is not None:
        results = [t for t in results if t.product_id == product_id]
    if supplier_id is not None:
        results = [t for t in results if t.supplier_id == supplier_id]
    return jsonify([t.to_dict() for t in results])


# modified create_transaction function to send a notification when a product's quantity_on_hand is at or below its reorder_level
@transactions_bp.route("", methods=["POST"])
def create_transaction():
    data = request.get_json()
    product = store.products.get(data["product_id"])
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    quantity = data["quantity"]
    tx_type = data["type"]

    if tx_type == "IN":
        product.quantity_on_hand += quantity
    elif tx_type == "OUT":
        product.quantity_on_hand -= quantity
    else:
        return jsonify({"error": "type must be IN or OUT"}), 400

    transaction_id = store.next_id("transaction")
    transaction = Transaction(
        id=transaction_id,
        product_id=data["product_id"],
        supplier_id=data.get("supplier_id"),
        type=tx_type,
        quantity=quantity,
    )
    store.transactions[transaction_id] = transaction

    response = transaction.to_dict()

    if tx_type == "OUT" and product.quantity_on_hand <= product.reorder_level:
        notification_sent = send_notification(
            "manager@example.com",
            "Low Stock Alert",
            f"Product {product.name} has only {product.quantity_on_hand} units remaining."
        )

        response["notification_sent"] = notification_sent

    return jsonify(response), 201

