
import frappe, json
from frappe import _
from .resolution import resolve_policy
from .engine import compute_slabbed, compute_bahrain_sio
from .utils import service_years
from .accounting import create_je

@frappe.whitelist()
def calculate_eos(employee, separation_type, last_working_date, wage_override=None):
    emp = frappe.get_doc("Employee", employee)
    res = resolve_policy(employee, last_working_date)
    policy = res["policy"]
    wage = float(wage_override) if wage_override else float(getattr(emp, "custom_last_wage", 0) or 0)
    svc = service_years(emp.date_of_joining, last_working_date, exclude_unpaid=int(policy.exclude_unpaid), employee=employee)

    if policy.mode == "SIO_BAHRAIN":
        gross = compute_bahrain_sio(policy, wage, svc)
        breakdown = [{"mode":"SIO","years":svc,"amount":gross}]
    else:
        gross, breakdown = compute_slabbed(policy, wage, svc, separation_type)

    doc = frappe.new_doc("EOS Calculation")
    doc.employee = employee
    doc.company = emp.company
    doc.country = res.get("country")
    doc.separation_type = separation_type
    doc.join_date = emp.date_of_joining
    doc.last_working_date = last_working_date
    doc.last_wage = wage
    doc.resolved_policy = policy.name
    doc.resolution_source = res.get("source_assignment")
    doc.resolution_explain = res.get("explain")
    doc.computed_years = svc
    doc.breakdown_json = json.dumps(breakdown, ensure_ascii=False, indent=2)
    doc.gross_eos = gross
    doc.net_payable = gross  # provisions_to_reverse can adjust later
    doc.status = "Calculated"
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "gross_eos": gross, "breakdown": breakdown}

@frappe.whitelist()
def post_eosb(calculation_name, reverse_provision=0.0, expense_account=None, provision_account=None, payable_account=None, posting_date=None, cost_center=None):
    calc = frappe.get_doc("EOS Calculation", calculation_name)
    settings = frappe.get_single("EOS Settings")
    expense = expense_account or settings.expense_account
    provision = provision_account or settings.provision_account
    payable = payable_account or settings.payable_account
    if not (expense and provision and payable):
        frappe.throw("Please set Expense/Provision/Payable accounts in EOS Settings or pass them to post_eosb.")

    je_name = create_je(
        company=calc.company,
        expense_acct=expense,
        provision_acct=provision,
        payable_acct=payable,
        amount=float(calc.gross_eos),
        posting_date=posting_date or frappe.utils.today(),
        cost_center=cost_center,
        reverse_provision=float(reverse_provision or 0.0)
    )
    calc.status = "Posted"
    calc.save(ignore_permissions=True)
    return {"journal_entry": je_name}
