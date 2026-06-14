import json
import os
from datetime import date

from clothing_erp.repositories.base_repository import BaseRepository
from clothing_erp.models.models import Product, Sale, SaleItem, Employee
from clothing_erp.config import DATA_DIR


class JSONRepository(BaseRepository):
    """Reads and writes data as JSON files inside the DATA_DIR folder."""

    def _path(self, filename: str) -> str:
        return os.path.join(DATA_DIR, filename)

    def _read(self, filename: str) -> list:
        path = self._path(filename)
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            return json.load(f)

    def _write(self, filename: str, data: list):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._path(filename), "w") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------ #
    # Products
    # ------------------------------------------------------------------ #
    def get_all_products(self) -> list:
        raw = self._read("products.json")
        return [
            Product(
                code=p["code"],
                name=p["name"],
                category=p["category"],
                sub_type=p["sub_type"],
                price=float(p["price"]),
                stock_qty=int(p["stock_qty"]),
            )
            for p in raw
        ]

    def update_stock(self, product_code: str, quantity_sold: int):
        raw = self._read("products.json")
        for p in raw:
            if p["code"] == product_code:
                p["stock_qty"] = int(p["stock_qty"]) - quantity_sold
                break
        self._write("products.json", raw)

    # ------------------------------------------------------------------ #
    # Employees
    # ------------------------------------------------------------------ #
    def get_all_employees(self) -> list:
        raw = self._read("employees.json")
        return [
            Employee(
                emp_id=e["emp_id"],
                name=e["name"],
                role=e["role"],
                salary=float(e["salary"]),
            )
            for e in raw
        ]

    # ------------------------------------------------------------------ #
    # Sales
    # ------------------------------------------------------------------ #
    def get_all_sales(self) -> list:
        raw = self._read("sales.json")
        products = {p.code: p for p in self.get_all_products()}
        sales = []
        for s in raw:
            items = [
                SaleItem(
                    product=products[i["product_code"]],
                    quantity=int(i["quantity"]),
                )
                for i in s["items"]
                if i["product_code"] in products
            ]
            sales.append(
                Sale(
                    sale_id=s["sale_id"],
                    date=date.fromisoformat(s["date"]),
                    items=items,
                    subtotal=float(s["subtotal"]),
                    tax=float(s["tax"]),
                    total=float(s["total"]),
                    billed_by=s["billed_by"],
                )
            )
        return sales

    def save_sale(self, sale: Sale):
        raw = self._read("sales.json")
        raw.append({
            "sale_id": sale.sale_id,
            "date": sale.date.isoformat(),
            "items": [
                {"product_code": si.product.code, "quantity": si.quantity}
                for si in sale.items
            ],
            "subtotal": sale.subtotal,
            "tax": sale.tax,
            "total": sale.total,
            "billed_by": sale.billed_by,
        })
        self._write("sales.json", raw)
    
    def record_attendance(self, emp_id: str, date: date, status: str):
        raw = self._read("attendance.json")
        raw.append({
            "emp_id": emp_id,
            "date": date.isoformat(),
            "status": status
        })
        self._write("attendance.json", raw) 

    def get_attendance_by_employee(self, emp_id: str):
        raw = self._read("attendance.json")
        return [r for r in raw if r["emp_id"] == emp_id]   
    
    def get_attendance_by_date(self, date: date):
        raw = self._read("attendance.json")
        return [r for r in raw if r["date"] == date.isoformat()]

    def get_sales_between_dates(self, start_date: date, end_date: date):
        raw = self._read("sales.json")
        products = {p.code: p for p in self.get_all_products()}
        sales = []
        for s in raw:
            sale_date = date.fromisoformat(s["date"])
            if start_date <= sale_date <= end_date:
                items = [
                    SaleItem(
                        product=products[i["product_code"]],
                        quantity=int(i["quantity"]),
                    )
                    for i in s["items"]
                    if i["product_code"] in products
                ]
                sales.append(
                    Sale(
                        sale_id=s["sale_id"],
                        date=sale_date,
                        items=items,
                        subtotal=float(s["subtotal"]),
                        tax=float(s["tax"]),
                        total=float(s["total"]),
                        billed_by=s["billed_by"],
                    )
                )
        return sales
      
    
 