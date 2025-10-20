
    frappe.ui.form.on('Employee', {
        refresh(frm) {
            frm.add_custom_button(__('Calculate EOS'), () => {
                frappe.prompt([
                    {label: 'Separation Type', fieldname: 'separation_type', fieldtype: 'Select', options: 'Termination
Resignation
Other', reqd: 1},
                    {label: 'Last Working Date', fieldname: 'last_working_date', fieldtype: 'Date', reqd: 1},
                    {label: 'Wage Override', fieldname: 'wage_override', fieldtype: 'Float'}
                ], (v) => {
                    frappe.call({
                        method: 'eos_gcc.eos.api.calculate_eos',
                        args: {
                            employee: frm.doc.name,
                            separation_type: v.separation_type,
                            last_working_date: v.last_working_date,
                            wage_override: v.wage_override
                        },
                        callback: (r) => {
                            if (r.message) {
                                frappe.msgprint(__('EOS Calculated: {0}', [r.message.gross_eos]));
                                frappe.set_route('Form', 'EOS Calculation', r.message.name);
                            }
                        }
                    });
                }, __('EOS Calculation'), __('Calculate'));
            });
        }
    });
