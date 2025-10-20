
import frappe
from dateutil.relativedelta import relativedelta
from datetime import date, datetime

def service_years(join_date: str, last_working_date: str, exclude_unpaid: int = 0, employee: str = None) -> float:
    jd = datetime.strptime(join_date, "%Y-%m-%d").date()
    lw = datetime.strptime(last_working_date, "%Y-%m-%d").date()
    days = (lw - jd).days
    if days < 0:
        return 0.0
    # TODO: subtract unpaid leave days if required (needs a query to Leave Application / Attendance)
    return round(days / 365.0, 6)

def months_to_amount(months: float, last_wage: float) -> float:
    # last_wage is monthly wage
    return months * last_wage

def days_to_amount(days: float, last_wage: float) -> float:
    # Assume 30-day month baseline
    return (days / 30.0) * last_wage
