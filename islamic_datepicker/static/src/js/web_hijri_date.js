odoo.define('islamic_datepicker.form_widgets', function (require) {
    "use strict";

    var core = require('web.core');
    var form_common = require('web.form_common');
    var FieldDate = core.form_widget_registry.get('date');
    var datepicker = require('web.datepicker') ;
    var DateWidget = datepicker.DateWidget;
    var DateTimeWidget = datepicker.DateTimeWidget;

    var _t = core._t;
    var l10n = _t.database.parameters;
    var Datefield = require('web.form_widgets');

    DateWidget.include({
        template: 'SlDatepicker'
        , events: {
            'click': function (e) {
            }
        , }
        , start: function () {
            this.$input = this.$('input.o_datepicker_input');
            this.$input_hijri = this.$el.find('input.oe_hijri');
            this.set_readonly(false);
            $('.removePicker').click(function () {
                this.$el.calendarsPicker.calendarsPicker({

                    calendar: $.calendars.instance('ummalqura', 'ar')
                    , dateFormat: 'dd - mm - yyyy'
                    , onSelect: this.convert_date_hijri,

                });
            });

        },

        get_value: function () {
            return this.get('value');
        }

    , destroy: function() {
        if(this.picker){
        this.picker.destroy();
        this._super.apply(this, arguments);
        }
    }

       ,parseArabic: function (str) {
    return Number( str.replace(/[٠١٢٣٤٥٦٧٨٩]/g, function(d) {
        return d.charCodeAt(0) - 1632;
    }).replace(/[۰۱۲۳۴۵۶۷۸۹]/g, function(d) {
        return d.charCodeAt(0) - 1776;
    }) );
}
        , convert_gregorian_hijri: function (text) {
            var text_split, year, month, day, calendar, calendar1, date;
            if (text) {
                if (text.indexOf('-') != -1) {
                    text_split = text.split('-');
                    year = parseInt(text_split[2]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[0]);
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar.toJD(year, month, day);
                    date = calendar1.fromJD(jd);

                }

                if (text.indexOf('/') != -1) {
                    text_split = text.split('/');
                    year = parseInt(text_split[2]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[0]);
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar.toJD(year, month, day);
                    date = calendar1.fromJD(jd);

                }

                return calendar1.formatDate('dd - mm - yyyy', date);
            }
        }
        ,set_value: function (value) {
                this.set({
                    'value': value
                });
        },

        set_readonly: function (readonly) {
            this._super(readonly);
            this.$input_hijri.prop('readonly', this.readonly);
        }
        , is_valid: function () {
            return true;
        }

        , set_value_from_ui: function () {
            // this._super();
            var value = this.$('.oe_datepicker_master').val() || "";
            var date = this.convert_gregorian_hijri(value);
            this.value = this.parse_client(date);
            this.set_value(this.parse_client(date));

        }

        , change_datetime: function (e) {

            this.set_value_from_ui();
            this.trigger("datetime_changed");
        }
        , convert_date_to_hijri: function (text) {
            var text_split, year, month, day, calendar, calendar1, date;
            if (text) {
                if (text.indexOf(' '))
                    text = text.split(' ')[0];
                if (text.indexOf('-') != -1) {
                    text_split = text.split('-');
                      year = parseInt(this.parseArabic(text_split[0]));
                    month = parseInt(this.parseArabic(text_split[1]));
                    day = parseInt(this.parseArabic(text_split[2]));

                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar.toJD(year, month, day);
                    date = calendar1.fromJD(jd);

                }

                if (text.indexOf('/') != -1 )  {
                    text_split = text.split('/');
                    year = parseInt(this.parseArabic(text_split[2]));
                    month = parseInt(this.parseArabic(text_split[1]));
                    day = parseInt(this.parseArabic(text_split[0]));
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    if (day)
                    var jd = calendar.toJD(year, month, day);
                    date =  day  ? calendar1.fromJD(jd) : false;

                }

                //                var m = (date.month() >= 10 ? date.month() : "0" + date.month());
                //                var d = (date.day() >= 10 ? date.day() : "0" + date.day());
                //

                return calendar1.formatDate('dd - mm - yyyy', date);
            }
        }
        ,render_value: function () {
            if (!this.get("effective_readonly")) {
                this.datewidget.set_value(this.get('value'));
            } else {

                this.$el.find("input").text(this.convert_gregorian_hijri(this.get('value')));
            }
        }
        ,set_value_from_server: function(value){
            this.set_value(value);
                        var self = this;
            if ( this.$el.parent().find('.geo_value').length > 0)
            this.$el.parent().find('.geo_value')[0].innerHTML ='' ;
            this.$('.oe_datepicker_container').datetimepicker({format: 'YYYY-MM-DD',
                                                               language : moment.locale(),
                                                               pickTime: false,
            useSeconds: false
            }).on('change.dp', function(e) {
                         self.$('.oe_datepicker_master').val(self.convert_date_to_hijri(this.value));
                         self.change_datetime();
                        }).val(value);
            this.$('.oe_datepicker_master').calendarsPicker({
                showAnim: 'slide'
                , showSpeed: 300
                , showOptions: {
                    direction: 'horizontal'
                }
                ,defaultDate: self.convert_date_to_hijri(self.get_value())
                , selectDefaultDate: true
                , calendar: $.calendars.instance('ummalqura', moment.locale())
                , dateFormat: 'dd - mm - yyyy'
                , onSelect: function (date) {
                    self.change_datetime();
                    self.$('.oe_datepicker_container').val(self.value);
                }
                , pickerClass: 'calandar_picker',
                 isRTL: true,
                renderer: $.extend({}, $.calendarsPicker.defaultRenderer, {
                    picker: $.calendarsPicker.defaultRenderer.picker.
                    replace(/\{link:clear\}/, '')
                })

            });
            
        }  
        , convert_gregorian_hijri: function (text) {
            var text_split, year, month, day, calendar, calendar1;
            if (text) {
                if (text.indexOf('-') != -1) {
                    text_split = text.split('-');
                    year = parseInt(text_split[2]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[0]);
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar1.toJD(year, month, day);
                    var date = calendar.fromJD(jd);

                }
                if (text.indexOf('/') != -1) {
                    text_split = text.split('/');
                    year = parseInt(text_split[2]);
                    month = parseInt(text_split[0]);
                    day = parseInt(text_split[1]);
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar1.toJD(year, month, day);
                    var date = calendar.fromJD(jd);

                }
                return calendar.formatDate('dd-mm-yyyy', date);

            }
            return '';
        }
    });

    FieldDate.include({


        convert_gregorian_hijri: function (text) {
            var text_split, year, month, day, calendar, calendar1;
            if (text) {
                if (text.indexOf('-') != -1) {
                    text_split = text.split('-');
                    year = parseInt(text_split[0]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[2]);
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar.toJD(year, month, day);
                    var date = calendar1.fromJD(jd);

                }
                if (text.indexOf('/') != -1) {
                    text_split = text.split('/');
                    year = parseInt(text_split[0]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[2]);
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar.toJD(year, month, day);
                    var date = calendar1.fromJD(jd);

                }
                 return (calendar1.formatDate( 'dd - mm - yyyy', date));

            }
            return '';
        }
        , render_value: function () {
                            var readonly = this.get('value') ? this.get('value') : '' ;
            if (!this.get("effective_readonly")) {
            var date_only = this.get('value')|| '' ;
                this.datewidget.set_value_from_server(date_only);
            } else {
                if(! this.$el.parent().find('.geo_value').length > 0){
                //first opening
                if (readonly.length > 0){
                this.$el.parent().append('<span class="geo_value">' +  '<span> / </span>' +readonly + '</span>') ;
                }
                }
                else
                    {
                    //update value
                    if (readonly.length > 0){
                    this.$el.parent().find('.geo_value')[0].innerHTML = '<span> / </span>' + readonly  ;
                    }

                    }
                this.$el.text(this.convert_gregorian_hijri(this.get('value')));
            }
        }
    , });

     DateTimeWidget.include({
      template: 'SlDateTimepicker',

        set_value_from_ui: function () {
            // this._super();
                       var value = this.$('.oe_datepicker_master').val() || "";
            var date = this.convert_gregorian_hijri(value);
            if (date.length > 0){
            var time = this.$('.sl_timepicker').val() || "";
            var dateTime = date.split(' ')[0]+' ' + time ;
            this.parse_client(dateTime);
            this.set_value(this.parse_client(dateTime));
            }

        },

        set_value_from_server: function(value){
            this.set_value(value);
                        var self = this;
            if ( this.$el.parent().find('.geo_value').length > 0)
            this.$el.parent().find('.geo_value')[0].innerHTML ='' ;

             var default_time = self.get_value().indexOf(' ') >0 ? value.split(' ')[1] : '' ;
             var default_date = self.get_value().indexOf(' ') >0 ? value.split(' ')[0] : '' ;
             $('.sl_timepicker').datetimepicker({
                    format: 'h:mm:ss',
                    startView: 1,
                    pickDate: false,
                    defaultDate: default_time,
//                    language : moment.locale(),
                    autoclose: true
                }).on("show", function(){
                $(".table-condensed .prev").css('visibility', 'hidden');
                $(".table-condensed .switch").text("Pick Time");
                $(".table-condensed .next").css('visibility', 'hidden');
                })
                .on('change.dp', function(e) {
                         self.change_datetime();
                        });
            this.$('.oe_datepicker_container').datetimepicker({format: 'YYYY-MM-DD',
                                                               language : moment.locale(),
                                                               pickTime: false,
                                                                      useSeconds: false

            }).on('change.dp', function(e) {
                         self.$('.oe_datepicker_master').val(self.convert_date_to_hijri(this.value));
                         self.change_datetime();
                        }).val(default_date);
            this.$('.oe_datepicker_master').calendarsPicker({
                showAnim: 'slide'
                , showSpeed: 300
                , showOptions: {
                    direction: 'horizontal'
                }
                ,defaultDate: self.convert_date_to_hijri(self.get_value())
                , selectDefaultDate: true
                , calendar: $.calendars.instance('ummalqura', moment.locale())
                , dateFormat: 'dd - mm - yyyy'
                , onSelect: function (date) {
                    self.change_datetime();
                    self.$('.oe_datepicker_container').val(self.get_value().split(' ')[0]);
                }
                , pickerClass: 'calandar_picker',
                 isRTL: true,
                renderer: $.extend({}, $.calendarsPicker.defaultRenderer, {
                    picker: $.calendarsPicker.defaultRenderer.picker.
                    replace(/\{link:clear\}/, '')
                })

            });

        }

    })



});