odoo.define('hijri_tree_date.tree_widgets', function (require) {
    "use strict";

    var listView = require('web.ListView')
    var core = require('web.core');
    var data = require('web.data');
    var DataExport = require('web.DataExport');
    var formats = require('web.formats');
    var Model = require('web.DataModel');
    var Pager = require('web.Pager');
    var pyeval = require('web.pyeval');
    var Sidebar = require('web.Sidebar');
    var utils = require('web.utils');
    var View = require('web.View');


    var List = listView.List.include({



    convert_gregorian_hijri: function(text) {

            if (text) {
                 if (text.indexOf('-')!= -1){
                    var text_split = text.split('-');
                    var year = parseInt(text_split[0]);
                    var month = parseInt(text_split[1]);
                    var day = parseInt(text_split[2]);
            var calendar = $.calendars.instance('gregorian');
                    var calendar1 = $.calendars.instance('ummalqura');
                    var jd = $.calendars.instance('gregorian').toJD(year,month,day);
                    var date = $.calendars.instance('ummalqura').fromJD(jd);
                 }
                if(text.indexOf('/')!= -1){
                    var text_split = text.split('/');
                   var year = parseInt(text_split[2]);
                    var month = parseInt(text_split[0]);
                    var day = parseInt(text_split[1]);
            var calendar = $.calendars.instance('gregorian');
                var    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar.toJD(year,month,day);
                    var date = calendar1.fromJD(jd);

                }
                return (calendar1.formatDate( 'dd - mm - yyyy', date));
            }
            return '';
        },


     render_cell: function (record, column) {
        var value;
        if(column.type === 'reference') {
            value = record.get(column.id);
            var ref_match;
            // Ensure that value is in a reference "shape", otherwise we're
            // going to loop on performing name_get after we've resolved (and
            // set) a human-readable version. m2o does not have this issue
            // because the non-human-readable is just a number, where the
            // human-readable version is a pair
            if (value && (ref_match = /^([\w\.]+),(\d+)$/.exec(value))) {
                // reference values are in the shape "$model,$id" (as a
                // string), we need to split and name_get this pair in order
                // to get a correctly displayable value in the field
                var model = ref_match[1],
                    id = parseInt(ref_match[2], 10);
                new data.DataSet(this.view, model).name_get([id]).done(function(names) {
                    if (!names.length) { return; }
                    record.set(column.id + '__display', names[0][1]);
                });
            }
          } else if(column.type === 'date') {
             value = record.get(column.id);
              var ww = this.convert_gregorian_hijri(value);
                 return ww;

        }
         else if(column.type === 'datetime') {
             if (record.get(column.id)){
             var vals = record.get(column.id).split(' ');
             var date = openerp.web.auto_str_to_date(record.get(column.id))  ;
             var hijriDate = this.convert_gregorian_hijri(vals[0]);
             var hijri_datetime = hijriDate +' ' + date.getHours() + ':' + date.getMinutes() +':' + date.getSeconds()  ;
             return hijri_datetime ;
             }
             return ' ';

}
        else if (column.type === 'many2one') {
            value = record.get(column.id);
            // m2o values are usually name_get formatted, [Number, String]
            // pairs, but in some cases only the id is provided. In these
            // cases, we need to perform a name_get call to fetch the actual
            // displayable value
            if (typeof value === 'number' || value instanceof Number) {
                // fetch the name, set it on the record (in the right field)
                // and let the various registered events handle refreshing the
                // row
                new data.DataSet(this.view, column.relation)
                        .name_get([value]).done(function (names) {
                    if (!names.length) { return; }
                    record.set(column.id, names[0]);
                });
            }
        } else if (column.type === 'many2many') {
            value = record.get(column.id);
            // non-resolved (string) m2m values are arrays
            if (value instanceof Array && !_.isEmpty(value)
                    && !record.get(column.id + '__display')) {
                var ids;
                // they come in two shapes:
                if (value[0] instanceof Array) {
                    _.each(value, function(command) {
                        switch (command[0]) {
                            case 4: ids.push(command[1]); break;
                            case 5: ids = []; break;
                            case 6: ids = command[2]; break;
                            default: throw new Error(_.str.sprintf( _t("Unknown m2m command %s"), command[0]));
                        }
                    });
                } else {
                    // 2. an array of ids
                    ids = value;
                }
                new Model(column.relation)
                    .call('name_get', [ids, this.dataset.get_context()]).done(function (names) {
                        // FIXME: nth horrible hack in this poor listview
                        record.set(column.id + '__display',
                                   _(names).pluck(1).join(', '));
                        record.set(column.id, ids);
                    });
                // temp empty value
                record.set(column.id, false);
            }
        }
        return column.format(record.toForm().data, {
            model: this.dataset.model,
            id: record.get('id')
        });
    },
    });

});