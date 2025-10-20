
import frappe
from .utils import service_years, months_to_amount, days_to_amount

def compute_slabbed(policy, last_wage: float, svc_years: float, separation_type: str):
    total = 0.0
    breakdown = []
    rules = frappe.get_all("EOS Rule", filters={"parent": policy.name}, fields="*")
    remaining = svc_years
    start = 0.0

    for r in rules:
        if r.applies_when != separation_type and r.applies_when != "Other":
            continue
        from_y = r.from_year or 0.0
        to_y = r.to_year or 0.0  # 0 = open-ended
        if remaining <= 0:
            break
        # overlap
        slab_start = max(start, from_y)
        slab_end = to_y if to_y > 0 else svc_years
        if slab_end <= slab_start:
            continue
        years_in_slab = min(remaining, slab_end - slab_start)
        if years_in_slab <= 0:
            continue

        # award
        amt = 0.0
        if r.award_unit == "MonthsPerYear":
            amt = months_to_amount(r.award_value * years_in_slab, last_wage)
        elif r.award_unit == "DaysPerYear":
            amt = days_to_amount(r.award_value * years_in_slab, last_wage)
        elif r.award_unit == "PercentOfAnnual":
            amt = (r.award_value / 100.0) * (last_wage * 12.0) * years_in_slab

        # resignation fraction
        frac = r.resignation_fraction or 1.0
        amt *= frac

        total += amt
        breakdown.append({
            "from_year": float(from_y),
            "to_year": float(to_y),
            "years": float(years_in_slab),
            "unit": r.award_unit,
            "value": float(r.award_value),
            "fraction": float(frac),
            "amount": round(amt,2)
        })
        remaining -= years_in_slab

    # apply cap if any
    if policy.max_cap_months:
        cap_amt = months_to_amount(policy.max_cap_months, last_wage)
        total = min(total, cap_amt)

    return round(total,2), breakdown

def compute_bahrain_sio(policy, last_wage: float, svc_years: float):
    # Simplified: 4.2% per year first 3 years, 8.4% thereafter, on annual base (12 * last_wage).
    annual = last_wage * 12.0
    y = svc_years
    first = min(y, 3.0)
    rest = max(0.0, y - 3.0)
    amt = (0.042 * annual * first) + (0.084 * annual * rest)
    return round(amt,2)
