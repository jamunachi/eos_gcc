
import frappe
import json
from datetime import date

def _priority_list():
    settings = frappe.get_single("EOS Settings")
    try:
        return json.loads(settings.priority_json.strip("'"))
    except Exception:
        return ["Employee","Cost Center","Department","Branch","Location","Company","Country"]

def get_priority_index(dim: str) -> int:
    order = _priority_list()
    dim = dim.strip()
    return order.index(dim) if dim in order else len(order)

def resolve_policy(employee: str, calc_date: str) -> dict:
    emp = frappe.get_doc("Employee", employee)
    company = emp.company
    country = frappe.db.get_value("Company", company, "country")

    ctx = {
        "Employee": emp.name,
        "Company": company,
        "Department": getattr(emp, "department", None),
        "Branch": getattr(emp, "branch", None),
        "Cost Center": getattr(emp, "custom_cost_center", None) or company,
        "Location": getattr(emp, "custom_location", None),
        "Country": country,
    }

    assigns = frappe.get_all(
        "EOS Policy Assignment",
        filters={
            "effective_from": ("<=", calc_date),
            "effective_to": ("in", [None, "", "0000-00-00", calc_date])  # very loose upper bound; we'll filter below
        },
        fields=["name","policy","company","target_type","target_name","priority_override","effective_from","effective_to"]
    )

    candidates = []
    for a in assigns:
        # company scoping
        if a.company and a.company != company:
            continue

        # active window
        ef = a.effective_from
        et = a.effective_to or "9999-12-31"
        if not (ef <= calc_date <= et):
            continue

        if a.target_type == "Company":
            matched = (a.company == company)
        elif a.target_type == "Country":
            pol_country = frappe.db.get_value("EOS Policy", a.policy, "country")
            matched = (pol_country == country)
        else:
            matched = (ctx.get(a.target_type) == a.target_name)

        if matched:
            precedence = get_priority_index(a.target_type)
            override = a.priority_override or 0
            candidates.append((precedence, -override, a.effective_from, a))

    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        chosen = candidates[0][3]
        policy = frappe.get_doc("EOS Policy", chosen.policy)
        return {
            "policy": policy,
            "source_assignment": chosen.name,
            "explain": f"Matched on {chosen.target_type}: {chosen.target_name or policy.country}",
            "country": country
        }

    # Fallback: any policy of the company country with latest effective_from
    pol = frappe.get_all("EOS Policy", filters={"country": country}, fields=["name","effective_from"], order_by="effective_from desc", limit_page_length=1)
    if pol:
        policy = frappe.get_doc("EOS Policy", pol[0].name)
        return {"policy": policy, "source_assignment": None, "explain": "Fallback: Country policy (latest)", "country": country}

    settings = frappe.get_single("EOS Settings")
    if settings.default_country:
        pol = frappe.get_all("EOS Policy", filters={"country": settings.default_country}, fields=["name","effective_from"], order_by="effective_from desc", limit_page_length=1)
        if pol:
            policy = frappe.get_doc("EOS Policy", pol[0].name)
            return {"policy": policy, "source_assignment": None, "explain": "Fallback: Settings default country", "country": settings.default_country}

    frappe.throw("No EOS Policy could be resolved. Please create an EOS Policy or a Policy Assignment.")
