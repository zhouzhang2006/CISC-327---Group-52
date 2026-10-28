class Product:
    def __init__(self, id, name, supplier_id, sku, unit_price, quantity_on_hand, reorder_level=0):
        self.id = id
        self.name = name
        self.supplier_id = supplier_id
        self.sku = sku
        self.unit_price = unit_price
        self.quantity_on_hand = quantity_on_hand
        self.reorder_level = reorder_level

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "supplier_id": self.supplier_id,
            "sku": self.sku,
            "unit_price": self.unit_price,
            "quantity_on_hand": self.quantity_on_hand,
            "reorder_level": self.reorder_level,
        }
