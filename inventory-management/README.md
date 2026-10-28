# Inventory Management System (IMS)

A small Flask REST API for tracking products, suppliers, and stock transactions.

Data is stored **in memory** (plain Python objects, no database) and is reset every time the app restarts. This project is meant to run before you've covered databases.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The API runs at `http://127.0.0.1:5000`.

## Web UI

Open `http://127.0.0.1:5000/` in a browser for a basic HTML front end (plain forms and tables, no JavaScript) to add/delete products and suppliers, and record stock transactions.

| Page         | Path               |
| ------------ | ------------------ |
| Home         | `/`                |
| Products     | `/ui/products`     |
| Suppliers    | `/ui/suppliers`    |
| Transactions | `/ui/transactions` |

This UI is separate from the JSON API below. It allows you to interact with the application without a REST client and uses the same in-memory store.

## Entities

- **Product:** `id`, `name`, `sku`, `unit_price`, `quantity_on_hand`
- **Supplier:** `id`, `name`, `contact_email`
- **Transaction:** `id`, `product_id`, `supplier_id`, `type` (IN/OUT), `quantity`, `transaction_date`

## JSON API Endpoints

| Method | Path                                     | Description                                                                                |
| ------ | ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| GET    | `/products`                              | List all products                                                                          |
| POST   | `/products`                              | Create a product with quantity validation (R13)                                            |
| GET    | `/products/<id>`                         | Get one product                                                                            |
| PUT    | `/products/<id>`                         | Update a product                                                                           |
| DELETE | `/products/<id>`                         | Delete a product                                                                           |
| GET    | `/products/<id>/stock-level`             | Current quantity on hand                                                                   |
| GET    | `/suppliers`                             | List all suppliers                                                                         |
| POST   | `/suppliers`                             | Create a supplier                                                                          |
| GET    | `/suppliers/<id>`                        | Get one supplier                                                                           |
| PUT    | `/suppliers/<id>`                        | Update a supplier                                                                          |
| DELETE | `/suppliers/<id>`                        | Delete a supplier                                                                          |
| POST   | `/transactions`                          | Record a stock movement (`product_id`, `type`: IN/OUT, `quantity`, optional `supplier_id`) |
| GET    | `/transactions?product_id=&supplier_id=` | Look up transactions                                                                       |
|  |

## Product Quantity Validation (R13)

The `POST /products` endpoint includes additional input validation to reduce errors when entering product quantities.

When creating a product, the `quantity_on_hand` field must be a non-negative integer (0 or greater).

**Valid quantities:**

- `0`
- `5`
- `100`

**Invalid quantities:**

- `-1` (negative integer)
- `"five"` (string)
- `2.5` (decimal)

If an invalid quantity is provided, the API returns HTTP `400 Bad Request` with the following JSON response:

```json
{
  "error": "Quantity must be a non-negative integer"
}
```

This enhancement prevents products from being created with invalid quantities, helping reduce inventory entry errors.

## Tests

Run all automated tests using:

```bash
python -m pytest -v
```

The tests cover existing inventory management functionality and the R13 quantity validation enhancement.
