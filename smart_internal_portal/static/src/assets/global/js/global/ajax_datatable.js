jQuery(function ($) {
    'use strict';

    var AjaxDatatables = function () {
        var $defaults = {
            time: "icon icon_clock",
            date: "icon icon_calendar",
            up: "icon arrow_carrot-up",
            down: "icon arrow_carrot-down",
            previous: 'icon arrow_carrot-left',
            next: 'icon arrow_carrot-right',
        };
        var datepicker = function () {
            //init date pickers
            $('.date-picker').datepicker({
                autoclose: true
            });
        }
        var ajaxdata = function () {
            $('#ajaxdatatable').DataTable({
                onSuccess: function (ajaxdata, e) {},
                onError: function (ajaxdata) {},
                onDataLoad: function (ajaxdata) {},
                loadingMessage: "Loading...",
                dataTable: {
                    bStateSave: !0,
                    lengthMenu: [
                        [10, 20, 50, 100, 150, -1],
                        [10, 20, 50, 100, 150, "All"]
                    ],
                    pageLength: 10,
                    ajax: {
                        url: "../../..//smart_internal_portal/static/src/assets/data/table_ajax.php"
                    },
                    order: [
                        [1, "asc"]
                    ]
                }
            });
            console.log('ajax data init');
        }
        return {
            init: function () {
                console.log('alert');
                datepicker();
                ajaxdata();
            }
        };
    }();
    jQuery(document).ready(function() {
        AjaxDatatables.init();
    });
});