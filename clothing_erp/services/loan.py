from clothing_erp.services.report_service import ReportService


class LoanService:
    def __init__(self, report_service: ReportService):
        self.report_service = report_service

    def get_loan_amount(self) -> float:
        return float(input("  Enter the loan amount (BDT): "))

    def show_loans(self, loan_amnt: float) -> dict:
        summary = self.report_service.get_sales_summary()
        revenue = summary["revenue"]
        remaining = revenue - loan_amnt
        return {
            "revenue": revenue,
            "loan": loan_amnt,
            "remaining": remaining,
        }
