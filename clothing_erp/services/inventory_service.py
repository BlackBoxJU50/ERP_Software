from clothing_erp.repositories.json_repository import JSONRepository
from clothing_erp.models.models import Product


class InventoryService:
    def __init__(self, repository: JSONRepository):
        self.repository = repository

    def get_all_products(self) -> list:
        return self.repository.get_all_products()

    def update_stock(self, product_code: str, quantity_sold: int):
        self.repository.update_stock(product_code, quantity_sold)
