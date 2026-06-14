from clothing_erp.repositories.json_repository import JSONRepository
from clothing_erp.models.models import Employee , AttendanceRecord
from clothing_erp.config import CURRENCY
from datetime import date
from clothing_erp.services.attendance_service import AttendanceService


class EmployeeService:
    def __init__(self, repository: JSONRepository):
        self.repository = repository

    def get_all_employees(self) -> list:
        return self.repository.get_all_employees()

    def calculate_payroll(self) -> dict:
        """Returns {employee_name: salary} using the salary stored in the data."""
        employees = self.repository.get_all_employees()
        return {emp.name: emp.salary for emp in employees}
    def record_attendance(self, emp_id: str, date: date, status: str):
        """Record attendance for an employee."""
        self.repository.record_attendance(emp_id, date, status)