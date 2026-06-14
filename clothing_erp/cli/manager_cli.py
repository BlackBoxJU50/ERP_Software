import uuid
from datetime import date

from clothing_erp.services.billing_service import BillingService
from clothing_erp.services.inventory_service import InventoryService
from clothing_erp.services.report_service import ReportService
from clothing_erp.services.employee_service import EmployeeService 
from clothing_erp.repositories.json_repository import JSONRepository
from clothing_erp.models.models import Sale, SaleItem , Employee, AttendanceRecord
from clothing_erp.config import CURRENCY, DB_BACKEND
from clothing_erp.services.loan import LoanService
from clothing_erp.services.attendance_service import AttendanceService


class ManagerCLI:
    def __init__(self):
        if DB_BACKEND == "json":
            repository = JSONRepository()
        # elif DB_BACKEND == "mysql":
        #     repository = MySQLRepository()
        self.billing_service = BillingService(repository)
        self.inventory_service = InventoryService(repository)
        self.report_service = ReportService(repository)
        self.employee_service = EmployeeService(repository)
        self.loan_service = LoanService(self.report_service)

    def run(self):
        while True:
            print("\n" + "=" * 40)
            print("       MANAGER DASHBOARD")
            print("=" * 40)
            print("1. View Inventory")
            print("2. View Sales Report")
            print("3. View Payroll")
            print("4. Make a Sale")
            print("5. Show Loans")
            print("6. Get Loan Amount")
            print("7. Give Attendance")
            print("8. Exit")
            print("-" * 40)
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.view_inventory()
            elif choice == "2":
                self.view_sales_report()
            elif choice == "3":
                self.view_payroll()
            elif choice == "4":
                self.make_sale()
            elif choice == "5":
                self.show_loans()
            elif choice == "6":
                self.get_loan_amount()
            elif choice == "7":
                print("Give Your Attendance")
                self.give_attendance()
                
            elif choice == "8": 
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    # ------------------------------------------------------------------ #
    def view_inventory(self):
        products = self.inventory_service.get_all_products()
        if not products:
            print("No products found.")
            return
        print("\n--- Inventory ---")
        print(f"{'Code':<10} {'Name':<25} {'Category':<15} {'Price':>10} {'Stock':>8}")
        print("-" * 72)
        for p in products:
            print(f"{p.code:<10} {p.name:<25} {p.category:<15} "
                  f"{p.price:>8.2f} {CURRENCY}  {p.stock_qty:>5}")

    # ------------------------------------------------------------------ #
    def view_sales_report(self):
        summary = self.report_service.get_sales_summary()
        print("\n--- Sales Summary ---")
        print("1. Full Report")
        print("2. Custom Report (Date Range)")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            print(f"  Total Transactions : {summary['total_sales']}")
            print(f"  Total Units Sold   : {summary['total_items']}")
            print(f"  Revenue (pre-tax)  : {summary['revenue']:.2f} {CURRENCY}")
            print(f"  Tax Collected (2%) : {summary['tax_collected']:.2f} {CURRENCY}")
            print(f"  Grand Total        : {summary['grand_total']:.2f} {CURRENCY}")
        elif choice == "2":
            try:
                start_str = input("Enter start date (YYYY-MM-DD): ").strip()
                end_str = input("Enter end date (YYYY-MM-DD): ").strip()
                start_date = date.fromisoformat(start_str)
                end_date = date.fromisoformat(end_str)
                summary = self.report_service.get_sales_summary_between_dates(start_date, end_date)
                print(f"  Total Transactions : {summary['total_sales']}")
                print(f"  Total Units Sold   : {summary['total_items']}")
                print(f"  Revenue (pre-tax)  : {summary['revenue']:.2f} {CURRENCY}")
                print(f"  Tax Collected (2%) : {summary['tax_collected']:.2f} {CURRENCY}")
                print(f"  Grand Total        : {summary['grand_total']:.2f} {CURRENCY}")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("Invalid choice. Please try again.")
        


    # ------------------------------------------------------------------ #
    def view_payroll(self):
        payroll = self.employee_service.calculate_payroll()
        if not payroll:
            print("No employees found.")
            return
        print("\n--- Payroll ---")
        total = 0.0
        for name, salary in payroll.items():
            print(f"  {name:<25} {salary:>10.2f} {CURRENCY}")
            total += salary
        print("-" * 42)
        print(f"  {'TOTAL':<25} {total:>10.2f} {CURRENCY}")

    # ------------------------------------------------------------------ #
    def make_sale(self):
        products = self.inventory_service.get_all_products()
        if not products:
            print("No products available.")
            return

        self.view_inventory()
        sale_items = []

        print("\nEnter items for this sale (blank product code to finish):")
        while True:
            code = input("  Product code: ").strip().upper()
            if not code:
                break
            product = next((p for p in products if p.code == code), None)
            if not product:
                print(f"  Product '{code}' not found. Try again.")
                continue
            try:
                qty = int(input(f"  Quantity (available: {product.stock_qty}): ").strip())
            except ValueError:
                print("  Invalid quantity. Try again.")
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
                  f"@ {item['unit_price']:.2f} = {item['total_price']:.2f} {CURRENCY}")
        print("-" * 55)
        print(f"  Subtotal : {invoice['subtotal']:.2f} {CURRENCY}")
        print(f"  Tax (2%) : {invoice['tax']:.2f} {CURRENCY}")
        print(f"  Total    : {invoice['total']:.2f} {CURRENCY}")

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
            billed_by="Manager",
        )
        self.billing_service.save_sale(sale)
        for item in sale_items:
            self.inventory_service.update_stock(item.product.code, item.quantity)
        print(f"Sale {sale.sale_id} saved successfully!")

    # ------------------------------------------------------------------ #
    def get_loan_amount(self):
        print("\n--- Get Loan Amount ---")
        try:
            loan_amnt = self.loan_service.get_loan_amount()
        except ValueError:
            print("  Invalid amount.")
            return
        result = self.loan_service.show_loans(loan_amnt)
        print(f"  Revenue          : {result['revenue']:.2f} {CURRENCY}")
        print(f"  Loan Deduction   : {result['loan']:.2f} {CURRENCY}")
        print(f"  Remaining        : {result['remaining']:.2f} {CURRENCY}")

    def show_loans(self):
        print("\n--- Loan Summary (enter loan to calculate) ---")
        try:
            loan_amnt = self.loan_service.get_loan_amount()
        except ValueError:
            print("  Invalid amount.")
            return
        result = self.loan_service.show_loans(loan_amnt)
        print(f"  Revenue          : {result['revenue']:.2f} {CURRENCY}")
        print(f"  Loan Deduction   : {result['loan']:.2f} {CURRENCY}")
        print(f"  Remaining        : {result['remaining']:.2f} {CURRENCY}")

    def give_attendance(self):
        print("\n--- Give Attendance ---")
        emp_id = input("  Employee ID: ").strip()
        today = date.today()
        status = input("  Status (Present/Absent): ").strip().capitalize()
        if status not in ["Present", "Absent"]:
            print("  Invalid status. Must be 'Present' or 'Absent'.")
            return
        self.employee_service.record_attendance(emp_id, today, status)
        print(f"Attendance for employee {emp_id} on {today} recorded as '{status}'.")


if __name__ == "__main__":
    manager_cli = ManagerCLI()
    manager_cli.run()