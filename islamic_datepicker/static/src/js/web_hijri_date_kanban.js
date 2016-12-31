odoo.define('islamic_datepicker', function (require) {
'use strict';

var kanban_widgets = require('web_kanban.widgets');

var DateTime = kanban_widgets.AbstractField.extend({
    start: function() {
        var datetime = this.formatDate(this.field.raw_value)
        var val = this.convert_gregorian_hijri(datetime);
        var $span = '<span >' + datetime.split(' ')[2]  +' '+ val  + '<span>';
        this.$el.append($span);
    },

     formatDate: function(date) {
      var hours = date.getHours();
      var minutes = date.getMinutes();

      minutes = minutes < 10 ? '0'+minutes : minutes;
      var strTime = hours + ':' + minutes ;
      return date.getMonth()+1 + "/" + date.getDate() + "/" + date.getFullYear() + "  " + strTime;
    },

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


});


kanban_widgets.registry.add('hijri_datetime', DateTime);

});