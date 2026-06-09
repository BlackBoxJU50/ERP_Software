import uuid
from datetime import date

from clothing_erp.services.billing_service import BillingService
from clothing_erp.services.inventory_service import InventoryService
from clothing_erp.repositories.json_repository import JSONRepository
from clothing_erp.models.models import Sale, SaleItem
from clothing_erp.config import CURRENCY, DB_BACKEND


class StaffCLI:
    def __init__(self):
        if DB_BACKEND == "json":
            repository = JSONRepository()
        self.billing_service = BillingService(repository)
        self.inventory_service = InventoryService(repository)

    def run(self):
        while True:
            print("\n" + "=" * 40)
            print("         STAFF PANEL")
            print("=" * 40)
            print("1. View Stock Levels")
            print("2. Make a Sale")
            print("3. Exit")
            print("-" * 40)
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.view_stock()
            elif choice == "2":
                self.make_sale()
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    # ------------------------------------------------------------------ #
    def view_stock(self):
        products = self.inventory_service.get_all_products()
        if not products:
            print("No products found.")
            return
        print("\n--- Stock Levels ---")
        print(f"{'Code':<10} {'Name':<25} {'In Stock':>10}")
        print("-" * 48)
        for p in products:
            status = "LOW" if p.stock_qty < 5 else ""
            print(f"{p.code:<10} {p.name:<25} {p.stock_qty:>8}  {status}")

    # ------------------------------------------------------------------ #
    def make_sale(self):
        products = self.inventory_service.get_all_products()
        if not products:
            print("No products available.")
            return

        self.view_stock()
        sale_items = []

        print("\nEnter items for this sale (blank product code to finish):")
        while True:
            code = input("  Product code: ").strip().upper()
            if not code:
                break
            product = next((p for p in products if p.code == code), None)
            if not product:
                print(f"  Product '{code}' not found.")
                continue
            try:
                qty = int(input(f"  Quantity (available: {product.stock_qty}): ").strip())
            except ValueError:
                print("  Invalid quantity.")
                continue
            if qty <= 0 or qty > product.stock_qty:
                print(f"  Invalid quantity. Must be 1–{product.stock_qty}.")
                continue
            sale_items.append(SaleItem(product=product, quantity=qty))

        if not sale_items:
            print("No items added. Sale cancelled.")
            return

        invoice = self.billing_service.calculate_invoice(sale_items)

        print("\n--- Invoice ---")
        for item in invoice["items"]:
            print(f"  {item['product_name']:<25} x{item['quantity']}  "
                  f"= {item['total_price']:.2f} {CURRENCY}")
        print("-" * 45)
        print(f"  Total (incl. 2% tax): {invoice['total']:.2f} {CURRENCY}")

        confirm = input("\nConfirm sale? (y/n): ").strip().lower()
        if confirm != "y":
            print("Sale cancelled.")
            return

        sale = Sale(
            sale_id=str(uuid.uuid4())[:8].upper(),
            date=date.today(),
            items=sale_items,
            subtotal=invoice["subtotal"],
            tax=invoice["tax"],
            total=invoice["total"],
            billed_by="Staff",
        )
        self.billing_service.save_sale(sale)
        for item in sale_items:
            self.inventory_service.update_stock(item.product.code, item.quantity)
        print(f"Sale {sale.sale_id} saved successfully!")


if __name__ == "__main__":
    staff_cli = StaffCLI()
    staff_cli.run()
