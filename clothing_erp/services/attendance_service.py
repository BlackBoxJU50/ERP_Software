from clothing_erp.models.models import AttendanceRecord

from datetime import date




class AttendanceService:
    def __init__(self):
        self.attendance_records = []  # This will store attendance records in-memory

    def record_attendance(self, emp_id: str, date: date, status: str):
        """Record attendance for an employee."""
        record = AttendanceRecord(emp_id=emp_id, date=date, status=status)
        self.attendance_records.append(record)

    def get_attendance_by_employee(self, emp_id: str):
        """Get all attendance records for a specific employee."""
        return [record for record in self.attendance_records if record.emp_id == emp_id]

    def get_attendance_by_date(self, date: date):
        """Get all attendance records for a specific date."""
        return [record for record in self.attendance_records if record.date == date]