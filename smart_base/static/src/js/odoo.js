odoo.define('smart_base.MyFieldBinaryFile', function (require) {
"use strict";

var core = require('web.core');

var FieldBinaryFile = core.form_widget_registry.get('binary');


/*
on choose file in field binary :  must put the name of file  in field_input_binary and not the binary data
*/

FieldBinaryFile.include({


    render_value: function() {
        var filename = this.view.datarecord[this.node.attrs.filename];
        if (this.get("effective_readonly")) {
            this.do_toggle(!!this.get('value'));
            if (this.get('value')) {
                this.$el.empty().append($("<span/>").addClass('fa fa-download'));
                if (filename) {
                    this.$el.append(" " + filename);
                }
            }
        } else {
            if(this.get('value')) {
                this.$el.children().removeClass('o_hidden');
                this.$('.o_select_file_button').first().addClass('o_hidden');
                this.$input.val(filename || this.filename || this.get('value')); //ADDED  : this.filename
            } else {
                this.$el.children().addClass('o_hidden');
                this.$('.o_select_file_button').first().removeClass('o_hidden');
            }
        }
    },

     on_file_uploaded: function(size, name, content_type, file_base64) {
        if (size === false) {
            this.do_warn(_t("File Upload"), _t("There was a problem while uploading your file"));
            // TODO: use openerp web crashmanager
        } else {
            this.filename = name;//ADDED
            this.on_file_uploaded_and_valid.apply(this, arguments);
        }
        this.$('.o_form_binary_progress').hide();
        this.$('button').show();
    },

});



});
