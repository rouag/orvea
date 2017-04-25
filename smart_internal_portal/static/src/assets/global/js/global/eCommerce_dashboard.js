!function (document, window, $) {
    "use strict";
    function chartistChart() {

        //simple line chart
        new Chartist.Line('.line-chartist', {
            labels: ['Mon', 'Tue', 'Wed', 'Thur', 'Fri'],
            series: [
                [12, 9, 7, 8, 5],
                [2, 1, 3.5, 7, 3],
                [1, 3, 4, 5, 6]
            ]
        }, {
            fullWidth: true,
            chartPadding: {
                right: 40
            }
        });

        //line chart with area
        new Chartist.Line('.line-with-area-chartist', {
            labels: [1, 2, 3, 4, 5, 6, 7],
            series: [
                [5, 9, 7, 8, 5, 3, 5]
            ]
        }, {
            low: 0,
            showArea: true
        });
    }
    $(window).on('resizeEnd', function () {
        chartistChart();
    });

    $(window).on('load', function () {
        chartistChart();
    });

    //create trigger to resizeEnd event
    $(window).resize(function () {
        if (this.resizeTO) clearTimeout(this.resizeTO);
        this.resizeTO = setTimeout(function () {
            $(this).trigger('resizeEnd');
        }, 500);
    });
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
