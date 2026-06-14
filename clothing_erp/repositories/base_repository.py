from abc import ABC, abstractmethod
from clothing_erp.models.models import Product, Sale, Employee
from datetime import date


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

    @abstractmethod
    def record_attendance(self, emp_id: str, date: date, status: str):
        pass

    @abstractmethod
    def get_attendance_by_employee(self, emp_id: str):
        pass

    @abstractmethod
    def get_attendance_by_date(self, date: date):
        pass

    @abstractmethod
    def get_sales_between_dates(self, start_date: date, end_date: date)-> list:
        pass
