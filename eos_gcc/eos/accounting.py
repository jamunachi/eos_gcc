
import frappe

def create_je(company, expense_acct, provision_acct, payable_acct, amount, posting_date, cost_center=None, reverse_provision=0.0):
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.company = company
    je.posting_date = posting_date

    lines = []

    # Reverse provision if any (Debit Provision, Credit Expense)
    if reverse_provision and reverse_provision > 0:
        lines.append({
            "account": provision_acct,
            "debit_in_account_currency": reverse_provision,
            "cost_center": cost_center
        })
        lines.append({
            "account": expense_acct,
            "credit_in_account_currency": reverse_provision,
            "cost_center": cost_center
        })

    # Recognize EOS expense and payable
    lines.append({
        "account": expense_acct,
        "debit_in_account_currency": amount,
        "cost_center": cost_center
    })
    lines.append({
        "account": payable_acct,
        "credit_in_account_currency": amount,
        "cost_center": cost_center
    })

    for l in lines:
        je.append("accounts", l)

    je.save(ignore_permissions=True)
    return je.name
