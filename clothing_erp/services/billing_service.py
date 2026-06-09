from clothing_erp.repositories.json_repository import JSONRepository
from clothing_erp.models.models import Product, Sale, SaleItem
from clothing_erp.config import TAX_RATE, CURRENCY


class BillingService:
    def __init__(self, repository: JSONRepository):
        self.repository = repository

    def get_all_products(self) -> list:
        return self.repository.get_all_products()

    def save_sale(self, sale: Sale):
        self.repository.save_sale(sale)

    def update_stock(self, product_code: str, quantity_sold: int):
        self.repository.update_stock(product_code, quantity_sold)

    def calculate_invoice(self, sale_items: list) -> dict:
        """
        Accepts a list of SaleItem objects and returns an invoice dict
        with itemised totals, subtotal, tax, and grand total.
        """
        invoice = {"items": [], "subtotal": 0.0, "tax": 0.0, "total": 0.0}
        for item in sale_items:
            invoice["items"].append({
                "product_code": item.product.code,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.product.price,
                "total_price": item.total_price,
            })
            invoice["subtotal"] += item.total_price

        invoice["tax"] = round(invoice["subtotal"] * TAX_RATE, 2)
        invoice["total"] = round(invoice["subtotal"] + invoice["tax"], 2)
        invoice["subtotal"] = round(invoice["subtotal"], 2)
        return invoice