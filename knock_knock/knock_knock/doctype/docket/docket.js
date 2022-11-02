// Copyright (c) 2022, efeone Software Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Docket', {
  refresh: function(frm){
    frm.set_df_property("due_date", "read_only", frm.is_new() ? 0 : 1);
    if (frm.doc.owner == frappe.session.user && !frm.is_new()){
      if (frm.doc.status == 'Open' || frm.doc.status == 'Overdue') {
        frm.set_df_property('change_due', 'hidden', 0)
      }
      else {
        frm.set_df_property('change_due', 'hidden', 1)
      }
    }
  },

  change_due : function(frm){
        let command = new frappe.ui.Dialog({
          title: 'Enter the reason',
          fields: [
             {
                label: 'New Date',
                fieldname: 'new_date',
                fieldtype: 'Datetime',
                reqd: 1
             },
             {
                  label: 'Reason',
                  fieldname: 'reason',
                  fieldtype: 'Small Text'
              },

          ],
          primary_action_label: 'Submit',
          primary_action(values) {
              command.hide();
              if(values){
                frappe.call({
                  method:'knock_knock.knock_knock.doctype.docket.docket.add_docket_comment',
                  args:{
                        'reason':values.reason,
                        'name':frm.doc.name,
                        'new_date': values.new_date
                       },
                  callback:function(r){
                    if (r) {
                      frm.reload_doc()
                    }
                  }
                })
              }
          }
      });
      command.show();
}
});
