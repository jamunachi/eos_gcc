
app_name = "eos_gcc"
app_title = "EOS GCC"
app_publisher = "Neotec Integrated Solutions"
app_description = "GCC End-of-Service (EOS/EOSB) calculator with policy engine and accruals"
app_icon = "octicon octicon-organization"
app_color = "blue"
app_email = "support@example.com"
app_version = "0.1.0"
app_license = "MIT"

fixtures = []

# Desk shortcuts
app_include_js = []
app_include_css = []

# Doctype JavaScript (Add Calculate EOS button via client script-like hook if needed later)
doctype_js = {
    # "Employee": "public/js/employee.js"
}

# Scheduler: monthly accruals
scheduler_events = {
    "monthly": [
        "eos_gcc.eos.accruals.post_monthly_accruals"
    ]
}

# Jinja globals (optional)
jinja = {
    "methods": [
        "eos_gcc.eos.api.calculate_eos",
    ]
}
