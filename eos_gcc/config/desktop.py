
from frappe import _

def get_data():
    return [{
        "module_name": "EOS GCC",
        "category": "Modules",
        "label": _("EOS GCC"),
        "color": "blue",
        "icon": "octicon octicon-organization",
        "type": "module",
        "description": "GCC End-of-Service (EOS/EOSB) calculator"
    }]
