from abc import ABC, abstractmethod
from clothing_erp.models.models import Product, Sale, Employee


class BaseRepository(ABC):

    @abstractmethod
    def get_all_products(self) -> list:
        pass

    @abstractmethod
    def get_all_employees(self) -> list:
        pass

    @abstractmethod
    def get_all_sales(self) -> list:
        pass

    @abstractmethod
    def save_sale(self, sale: Sale):
        pass

    @abstractmethod
    def update_stock(self, product_code: str, quantity_sold: int):
        pass