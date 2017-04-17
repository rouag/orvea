odoo.define('islamic_datepicker_entreprise.ummalqura_date_widget', function(require) {
    var Model = require('web.Model');
    var core = require('web.core');
    var _t = core._t;
    var time = require('web.time');
    var ListView = core.view_registry.get('list')
    var FieldDateTime = core.form_widget_registry.get('datetime');
    var FieldDate = core.form_widget_registry.get('date');
    var datepicker = require('web.datepicker');
    var formats = require('web.formats');
    var data = require('web.data');
    var res_users = new Model("res.users");
    var lang = '';
    var date_format = '';
    res_users.call("datepicker_localization", []).then(function(result) {
        lang = result['lang'];
        date_format = result['date_format'];
        date_format = date_format.replace(/%(.)/g, "$1$1").toLowerCase();;
    });

    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////
    /////////////////       ListView      //////////////////////
    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////
    ListView.List.include({
        parseArabic: function(str) {
            return Number(str.replace(/[٠١٢٣٤٥٦٧٨٩]/g, function(d) {
                return d.charCodeAt(0) - 1632;
            }).replace(/[۰۱۲۳۴۵۶۷۸۹]/g, function(d) {
                return d.charCodeAt(0) - 1776;
            }));
        },
        convert_gregorian_hijri: function(text) {
        // console.log(arguments.callee.name);
            if (text) {
             console.log('--------text1-----',text);
                text = moment(text, date_format)._i;

                if (text.indexOf('-') != -1) {
                    text_split = text.split('-');
                    year = parseInt(this.parseArabic(text_split[2]));
                    month = parseInt(this.parseArabic(text_split[1]));
                    day = parseInt(this.parseArabic(text_split[0]));

                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = $.calendars.instance('gregorian').toJD(year, month, day);
                    var date = $.calendars.instance('ummalqura').fromJD(jd);

                    return (calendar1.formatDate('dd-mm-yyyy', date));
                }
                if (text.indexOf('/') != -1) {
                    text_split = text.split('/');

                    console.log('--------text_splittext_split-----',text_split);

                  //  year = this.parseArabic(text_split[2]);
                    year_text=  text_split[2].substring(0, 4);
                    year =parseInt(this.parseArabic(year_text));
                    month = parseInt(this.parseArabic(text_split[1]));
                    day = parseInt(this.parseArabic(text_split[0]));
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');

                    console.log('--------fun year,month,day-----',year,month,day);

                    var jd = calendar.toJD(year, month, day);
                    var date = calendar1.fromJD(jd);
                    return (calendar1.formatDate('dd-mm-yyyy', date));
                }
                return '';

            }
            return '';
        },
        render_cell: function(record, column) {
        // console.log(arguments.callee.name);
            var value;
            if (column.type === 'date' || column.type === 'datetime') {
                var res = column.format(record.toForm().data, {
                    model: this.dataset.model,
                    id: record.get('id')
                });
                return moment(res, date_format)._i + "&nbsp; &nbsp; &nbsp;" + this.convert_gregorian_hijri(column.format(record.toForm().data, {
                    model: this.dataset.model,
                    id: record.get('id')
                }));
            } else if (column.type === 'reference') {
                value = record.get(column.id);
                var ref_match;
                if (value && (ref_match = /^([\w\.]+),(\d+)$/.exec(value))) {
                    var model = ref_match[1],
                        id = parseInt(ref_match[2], 10);
                    new data.DataSet(this.view, model).name_get([id]).done(function(names) {
                        if (!names.length) {
                            return;
                        }
                        record.set(column.id + '__display', names[0][1]);
                    });
                }
            } else if (column.type === 'many2one') {
                value = record.get(column.id);

                if (typeof value === 'number' || value instanceof Number) {

                    new data.DataSet(this.view, column.relation)
                        .name_get([value]).done(function(names) {
                            if (!names.length) {
                                return;
                            }
                            record.set(column.id, names[0]);
                        });
                }
            } else if (column.type === 'many2many') {
                value = record.get(column.id);
                if (value instanceof Array && !_.isEmpty(value) && !record.get(column.id + '__display')) {
                    var ids;
                    if (value[0] instanceof Array) {
                        _.each(value, function(command) {
                            switch (command[0]) {
                                case 4:
                                    ids.push(command[1]);
                                    break;
                                case 5:
                                    ids = [];
                                    break;
                                case 6:
                                    ids = command[2];
                                    break;
                                default:
                                    throw new Error(_.str.sprintf(_t("Unknown m2m command %s"), command[0]));
                            }
                        });
                    } else {
                        ids = value;
                    }
                    new Model(column.relation)
                        .call('name_get', [ids, this.dataset.get_context()]).done(function(names) {

                            record.set(column.id + '__display',
                                _(names).pluck(1).join(', '));
                            record.set(column.id, ids);
                        });
                    record.set(column.id, false);
                }
            }
            return column.format(record.toForm().data, {
                model: this.dataset.model,
                id: record.get('id')
            });
        },
    });




    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////
    /////////////////       Datepicker      ////////////////////
    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////

    datepicker.DateWidget.include({

        init: function(parent, options) {
        // console.log(arguments.callee.name);
            this._super.apply(this, arguments);
            var l10n = _t.database.parameters;

            this.name = parent.name;
            this.options = _.defaults(options || {}, {
                pickTime: this.type_of_date === 'datetime',
                useSeconds: this.type_of_date === 'datetime',
                startDate: moment({
                    y: 1900
                }),
                endDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down'
                },
                // Must disable language to use arabic number
                //language: moment.locale(),
                format: time.strftime_to_moment_format((this.type_of_date === 'datetime') ? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
            });
        },
        start: function() {
        // console.log(arguments.callee.name);
            var self = this;
            //            this.$input = this.$el.find('input.oe_simple_date');
            //            this.$input_picker = this.$el.find('input.oe_datepicker_container');
            //            this.$input_hijri = this.$el.find('input.oe_hijri');
            //            $(this.$input_hijri).val('')
            //            // this._super();
            //
            //            this.$input = this.$el.find('input.oe_simple_date');
            this.$input = this.$('input.o_datepicker_input');

            this.$input_hijri = this.$el.find('input.oe_hijri');
            console.log('----------------------',this.$input_hijri);
            this.set_readonly(false);

            this.$input = this.$('input.oe_datepicker_master');
            this.$input.datetimepicker(this.options);

            this.picker = this.$input.data('DateTimePicker');
            this.set_readonly(false);
            this.set_value(false);
            this.$input_hijri.calendarsPicker({
                calendar: $.calendars.instance('ummalqura', 'ar'),
                dateFormat: 'dd-mm-yyyy',
                onSelect: convert_date_hijri,
                isRTL: true,
            });

            //this._super();
            function convert_date_hijri(date) {
            // console.log(arguments.callee.name);
                try {
                    if (!date) {
                        return false
                    }
                    // console.log("date-----click here---------", parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()));
                    if (self.__parentedParent.field.type == 'datetime') {
                        var jd = $.calendars.instance('ummalqura').toJD(parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()) + 1);
                        var date = $.calendars.instance('gregorian').fromJD(jd);
                        var date_value = new Date(parseInt(date.year()), parseInt(date.month()) - 1, parseInt(date.day()));
                        if (self.$input.val()) {
                            self.$input.val($.datepicker.formatDate(date_format + ' ' + self.$input.val().split(' ')[1], date_value));
                        } else {
                            self.$input.val($.datepicker.formatDate(date_format + ' 00:00:00', date_value));
                        }
                    } else {
                        var jd = $.calendars.instance('ummalqura').toJD(parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()));
                        var date = $.calendars.instance('gregorian').fromJD(jd);
                        var date_value = new Date(parseInt(date.year()), parseInt(date.month()) - 1, parseInt(date.day()));
                        self.$input.val($.datepicker.formatDate(date_format, date_value));

                    }
                    var test_tree_view = self.__parentedParent.field_manager.fields_view.arch.attrs.editable;
                    // TODO check when tree view is editable bottom or top
                    if (test_tree_view === 'bottom' || test_tree_view === 'top') {
                        //self.change_datetime();
                        self.set_value_from_ui();
                    } else {
                        self.change_datetime();
                    }
                } catch (e) {
                    return false;
                }
            }
        },
        set_value: function(value) {
        // console.log(arguments.callee.name);
            //            this._super(value);
            $(this.$input_hijri).val('');
            var dateHijri = this.convert_gregorian_hijri(value);
            $(this.$input_hijri).val(dateHijri);
            //this.$input.val(value ? value : '');
            this.$input.val(value ? this.format_client(value) : '');
            this.set({
                'value': value
            });

        },
        convert_gregorian_hijri: function(text) {
        // console.log(arguments.callee.name);
            if (text) {
                text = moment(text, date_format)._i;
                if (text.indexOf('-') != -1) {
                    text_split = text.split('-');
                    year = parseInt(this.parseArabic(text_split[0]));
                    month = parseInt(this.parseArabic(text_split[1]));
                    day = parseInt(this.parseArabic(text_split[2]));
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = $.calendars.instance('gregorian').toJD(year, month, day);
                    var date = $.calendars.instance('ummalqura').fromJD(jd);
                }
                if (text.indexOf('/') != -1) {
                    text_split = text.split('/');
                    year = parseInt(this.parseArabic(text_split[2]));
                    month = parseInt(this.parseArabic(text_split[0]));
                    day = parseInt(this.parseArabic(text_split[1]));
                    calendar = $.calendars.instance('gregorian');
                    calendar1 = $.calendars.instance('ummalqura');
                    var jd = calendar.toJD(year, month, day);
                    var date = calendar1.fromJD(jd);
                }
                return (calendar1.formatDate('dd-mm-yyyy', date));
            }
            return '';
        },
        parseArabic: function(str) {
            return Number(str.replace(/[٠١٢٣٤٥٦٧٨٩]/g, function(d) {
                return d.charCodeAt(0) - 1632;
            }).replace(/[۰۱۲۳۴۵۶۷۸۹]/g, function(d) {
                return d.charCodeAt(0) - 1776;
            }));
        },
        set_value_from_ui: function() {
        // console.log(arguments.callee.name);
            this._super();
            var value = this.$input.val() || false;
            this.value = this.parse_client(value);
            this.convert_gregorian_hijri(this.value);
        },
        set_readonly: function(readonly) {
        // console.log(arguments.callee.name);
            this._super(readonly);
            this.$input_hijri.prop('readonly', this.readonly);
        },
        change_datetime: function(e) {
        // console.log(arguments.callee.name);
            this.set_value_from_ui();
            this.trigger("datetime_changed");
        },
        destroy: function() {
        // console.log(arguments.callee.name);
            if (this.picker) {
                this.picker.destroy();
                this._super.apply(this, arguments);
            }
        }
    });
    /*    FieldDateTime.include({

            initialize_content: function() {

                if (!this.get("effective_readonly")) {
                    this.datewidget = this.build_widget();
                    this.datewidget.on('datetime_changed', this, _.bind(function() {
                        this.internal_set_value(this.datewidget.get_value());
                    }, this));
                    this.datewidget.appendTo(this.$el.find(".oe_simple_date")[0]);
                    this.setupFocus(this.datewidget.$input);
                    this.format = "%m/%d/%Y";
                    showtime = false;
                    this.calendar_format = this.field.type;

                    this.datewidget.calendar_format = this.field.type;
                    if (this.field.type == 'datetime') {
                        this.format = "%m/%d/%Y %H:%M:%S";
                        showtime = true
                    }
                    var self = this;

                    function convert_date_hijri(date) {
                        // console.log("date-----click here---------", parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()));
                        if (!date) {
                            return false
                        }
                        if (self.field.type == 'datetime') {
                            var jd = $.calendars.instance('ummalqura').toJD(parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()) + 1);
                            var date = $.calendars.instance('gregorian').fromJD(jd);
                            var date_value = new Date(parseInt(date.year()), parseInt(date.month()) - 1, parseInt(date.day()));
                            self.datewidget.$input.val($.datepicker.formatDate(date_format + ' 00:00:00', date_value));
                        } else {
                            var jd = $.calendars.instance('ummalqura').toJD(parseInt(date[0].year()), parseInt(date[0].month()), parseInt(date[0].day()));
                            var date = $.calendars.instance('gregorian').fromJD(jd);
                            var date_value = new Date(parseInt(date.year()), parseInt(date.month()) - 1, parseInt(date.day()));
                            self.datewidget.$input.val($.datepicker.formatDate(date_format, date_value));

                        }
                        self.datewidget.change_datetime();
                    }

                    $(".o_datepicker input:last").click(function(event) {
                        event.stopPropagation();
                        $('.oe_hijri').calendarsPicker({
                            calendar: $.calendars.instance('ummalqura', lang),
                            dateFormat: 'dd - mm - yyyy',
                            onSelect: convert_date_hijri,
                        });
                    });
                    $('.oe_hijri').calendarsPicker({
                        calendar: $.calendars.instance('ummalqura', lang),
                        dateFormat: 'dd - mm - yyyy',
                        onSelect: convert_date_hijri,
                    });
                }
                this.calendar_format = this.field.type;
            },
            convert_gregorian_hijri: function(text) {
                if (text) {
                    text = moment(text, date_format)._i;
                    if (text.indexOf('-') != -1) {
                        text_split = text.split('-');
                        year = parseInt(text_split[0]);
                        month = parseInt(text_split[1]);
                        day = parseInt(text_split[2]);
                        calendar = $.calendars.instance('gregorian');
                        calendar1 = $.calendars.instance('ummalqura');
                        var jd = $.calendars.instance('gregorian').toJD(year, month, day);
                        var date = $.calendars.instance('ummalqura').fromJD(jd);
                    }
                    if (text.indexOf('/') != -1) {
                        text_split = text.split('/');
                        year = parseInt(text_split[2]);
                        month = parseInt(text_split[0]);
                        day = parseInt(text_split[1]);
                        calendar = $.calendars.instance('gregorian');
                        calendar1 = $.calendars.instance('ummalqura');
                        var jd = calendar.toJD(year, month, day);
                        var date = calendar1.fromJD(jd);
                    }
                    return (calendar1.formatDate('dd - mm - yyyy', date));
                }
                return '';
            },

            render_value: function() {
                if (!this.get("effective_readonly")) {
                    // console.log('this.datewidget');
                    // console.log(this.datewidget);
                    this.datewidget.set_value(this.get('value'));
                } else {
                    var date_value = openerp.web.format_value(this.get('value'), this, '');
                    this.$el.find(".oe_simple_date").text(date_value);
                    this.$el.find(".oe_hijri_date").text(this.convert_gregorian_hijri(this.get('value')));
                }
            }
        });*/




    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////
    ///////////////       FieldDateTime      ///////////////////
    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////
    FieldDateTime.include({

        convert_gregorian_hijri: function(text) {
        // console.log(arguments.callee.name);
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
                return (calendar1.formatDate('dd - mm - yyyy', date));

            }
            return '';
        },
        render_value: function() {
        // console.log(arguments.callee.name);
            var date_readonly = this.get('value') ? this.get('value') : '';
            date_readonly = openerp.web.format_value(this.get('value'), this, '');
            //date_readonly=moment(date_readonly).format(date_format);
            date_readonly = moment(date_readonly, date_format)._i;
            if (!this.get("effective_readonly")) {
                var date_only = this.get('value') || '';
                date_only = moment(date_only, date_format)._i;
                this.$el.parent().find('.gregorian_datetime_value').remove();
                this.datewidget.set_value(date_only);
                //                this.datewidget.set_value_from_server(date_only);
            } else {
                // check field visibility
                if (!this.$el.parent().find('.gregorian_datetime_value').length > 0) {
                    //first opening
                    if (date_readonly.length > 0) {
                        this.$el.parent().append('<span class="gregorian_datetime_value ' + this.$el.attr("class") + '">' + '<span>   /   </span>' + date_readonly + '</span>');
                    }
                } else {
                    //update value
                    if (date_readonly.length > 0) {
                        this.$el.parent().find('.gregorian_datetime_value')[0].innerHTML = '<span>   /   </span>' + date_readonly;
                    }

                }
                this.$el.text(this.convert_gregorian_hijri(this.get('value')));

            }
        },
    });




    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////
    /////////////////       FieldDate      /////////////////////
    ////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////



    FieldDate.include({


        convert_gregorian_hijri: function(text) {
        // console.log(arguments.callee.name);
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
                return (calendar1.formatDate('dd-mm-yyyy', date));

            }
            return '';
        },
        render_value: function() {
        // console.log(arguments.callee.name);
            var date_readonly = this.get('value') ? this.get('value') : '';
            date_readonly = openerp.web.format_value(this.get('value'), this, '');
            //date_readonly=moment(date_readonly).format(date_format);
            date_readonly = moment(date_readonly, date_format)._i;
            //this.datewidget.set_value(date_only);
            if (!this.get("effective_readonly")) {
                var date_only = this.get('value') || '';
                date_only = moment(date_only, date_format)._i;
                this.$el.parent().find('.gregorian_value').remove();
                this.datewidget.set_value(date_only);
                //                this.datewidget.set_value_from_server(date_only);
            } else {
                //var date_value = openerp.web.format_value(this.get('value'), this, '');
                //// console.log(date_value);
                if (!this.$el.parent().find('.gregorian_value').length > 0) {
                    //first opening
                    if (date_readonly.length > 0) {
                        this.$el.parent().append('<span class="gregorian_value ' + this.$el.attr("class") + '">' + '<span>   /   </span>' + date_readonly + '</span>');
                    }
                } else {
                    //update value
                    if (date_readonly.length > 0) {
                        this.$el.parent().find('.gregorian_value')[0].innerHTML = '<span>   /   </span>' + date_readonly;
                    }

                }
                this.$el.text(this.convert_gregorian_hijri(this.get('value')));
            }
        },
    });


});