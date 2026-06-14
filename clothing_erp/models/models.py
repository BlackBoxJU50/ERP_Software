from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Product:
    code: str
    name: str
    category: str
    sub_type: str
    price: float
    stock_qty: int


@dataclass
class SaleItem:
    product: Product
    quantity: int
    total_price: float = field(init=False)

    def __post_init__(self):
        self.total_price = self.product.price * self.quantity


@dataclass
class Sale:
    sale_id: str
    date: date
    items: list  # list[SaleItem]
    subtotal: float
    tax: float
    total: float
    billed_by: str

# i want to track how many items are sold in a month


@dataclass(frozen=True)
class Employee:
    emp_id: str
    name: str
    role: str
    salary: float
   

@dataclass
class AttendanceRecord:
    emp_id: str
    date: date
    status: str  
