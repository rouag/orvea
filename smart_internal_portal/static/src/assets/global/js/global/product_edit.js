!function (document, window, $) {
    "use strict";

    $(".check_all").change(function () {
        var $this = $(this),
            $checkbox = $this.closest('.check_all').find('[type="checkbox"]');
        $checkbox.is(":checked") ? $this.closest('table').closest('.dataTables_scroll').find('.mail_message .checkbox').children('label').addClass("checked").find('input[type="checkbox"]').prop('checked', true) : $this.closest('table').closest('.dataTables_scroll').find('.mail_message .checkbox').children('label').removeClass("checked").find('input[type="checkbox"]').prop('checked', false)
         });
    $('.mail_message .checkbox').change(function () {
        var $this = $(this),
            $checkvalue = $this.find('[type="checkbox"]');
        $checkvalue.is(":checked") ? $checkvalue.parents('label').addClass("checked") : $checkvalue.parents('label').removeClass("checked");
        $this.find('[type="checkbox"]').length == $this.find('[type="checkbox"]:checked').length ? $this.closest('table').closest('.dataTables_scroll').find(".check_all").children('label').addClass('checked').find('input[type="checkbox"]').prop('checked', true) : $this.closest('table').closest('.dataTables_scroll').find(".check_all").children('label').removeClass('checked').prop('checked', false);
    });

    $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
        $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
    } );


    /*---- Date-time-picker ----*/
    var $defaults = {
        time: "icon icon_clock",
        date: "icon icon_calendar",
        up: "icon arrow_carrot-up",
        down: "icon arrow_carrot-down",
        previous: 'icon arrow_carrot-left',
        next: 'icon arrow_carrot-right',
    };

    $(".check_all").on('change', function (e) {
        var $this = $(this);
        if ($this.is(':checked') === true) {
            $this.parents('div.dataTables_wrapper').find('[type="checkbox"]').prop('checked', true);
        }
        else {
            $this.parents('div.dataTables_wrapper').find('[type="checkbox"]').prop('checked', false);
        }
    });

}(document, window, jQuery);