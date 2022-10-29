// Copyright (c) 2022, efeone Software Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Docket', {
  refresh: function(frm){
    frm.set_df_property("due_date", "read_only", frm.is_new() ? 0 : 1);
    frm.set_df_property("change_due", "hidden", frm.is_new() ? 1 : 0);
  },

  change_due : function(frm){
  let command = new frappe.ui.Dialog({
      title: 'Enter the reason',
      fields: [
          {
              label: 'Reason',
              fieldname: 'reason',
              fieldtype: 'Small Text'
          },
      ],
      primary_action_label: 'Submit',
      primary_action(values) {
          command.hide();
          if(values.reason){
            frappe.call({
              method:'knock_knock.knock_knock.doctype.docket.docket.add_docket_comment',
              args:{
                    'reason':values.reason,
                    'name':frm.doc.name
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
