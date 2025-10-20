
import frappe
from frappe.utils import nowdate
from .resolution import resolve_policy
from .engine import compute_slabbed, compute_bahrain_sio
from .utils import service_years
from .accounting import create_je

def _derive_last_wage(emp, policy):
    # Try Salary Structure Assignment (last base), fallback to employee custom field
    # Simplified: pull from Employee.custom_last_wage if exists
    wage = getattr(emp, "custom_last_wage", None)
    if not wage:
        # as last resort default 0 to avoid crash
        wage = 0.0
    return float(wage)

def post_monthly_accruals():
    # For each company with EOS Accrual Method, compute total accrual and post JE
    methods = frappe.get_all("EOS Accrual Method", fields="*")
    for m in methods:
        company = m.company
        expense = m.expense_account
        provision = m.provision_account
        # payable not used for accrual; accrual goes to provision
        # gather employees in the company (Active)
        employees = frappe.get_all("Employee", filters={"company": company, "status": "Active"}, fields=["name","date_of_joining"])
        total = 0.0
        for e in employees:
            try:
                res = resolve_policy(e.name, frappe.utils.today())
                pol = res["policy"]
                emp = frappe.get_doc("Employee", e.name)
                wage = _derive_last_wage(emp, pol)
                svc = service_years(emp.date_of_joining, frappe.utils.today(), exclude_unpaid=int(pol.exclude_unpaid), employee=emp.name)

                if pol.mode == "SIO_BAHRAIN":
                    # annual entitlement proportionally accrued monthly
                    annual = compute_bahrain_sio(pol, wage, 1.0)  # one year
                    monthly_accrual = annual / 12.0
                else:
                    # simple approach: compute expected annual EOS growth by slabs; here approximate as 1 year increment
                    one_year, _ = compute_slabbed(pol, wage, 1.0, "Termination")
                    monthly_accrual = one_year / 12.0

                total += monthly_accrual
            except Exception:
                continue

        if total > 0:
            # Post a single JE per company: Debit Expense, Credit Provision
            je = frappe.new_doc("Journal Entry")
            je.voucher_type = "Journal Entry"
            je.company = company
            je.posting_date = nowdate()
            je.append("accounts", {"account": expense, "debit_in_account_currency": total})
            je.append("accounts", {"account": provision, "credit_in_account_currency": total})
            je.save(ignore_permissions=True)
            frappe.db.commit()
