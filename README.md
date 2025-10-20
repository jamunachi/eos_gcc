
# EOS GCC (End of Service for GCC Countries)

A small ERPNext/Frappe app that computes End-of-Service (EOS/EOSB) for KSA, UAE, Qatar, Oman, Kuwait, and Bahrain.
- Policy engine with effective dates
- Assign policy by Employee/Cost Center/Department/Branch/Location/Company/Country (with priority)
- One-click calculation on Employee
- Monthly accruals and EOSB posting (Journal Entry draft)
- Explainable breakdown and audit trail

## Install
```bash
bench get-app /path/to/eos_gcc
bench --site your.site install-app eos_gcc
```

## Quick Start
1) Open **EOS Settings** to confirm priority order and defaults.
2) Seed or create **EOS Policies** per country.
3) Create **EOS Policy Assignments** for Company/Branches/etc.
4) On Employee, click **Calculate EOS** (Action button) to produce an **EOS Calculation**.
5) Use **Create Journal Entry (Draft)** to book EOSB.
6) Enable scheduler; monthly accrual job posts provision entries.

> This skeleton ships with minimal fields and code; extend as needed.
