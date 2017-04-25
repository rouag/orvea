$(function () {
    "use strict";
    $('#individualcolumn tfoot th').each(function () {
        var title = $(this).text();
        $(this).html('<input type="text" class="form-control" placeholder="Search ' + title + '" />');
    });

    // DataTable
    var individualcolumn = $('#individualcolumn').DataTable({
        "oLanguage": {
            "oPaginate": {
                "sFirst": "<", // This is the link to the first page
                "sPrevious": "«", // This is the link to the previous page
                "sNext": "»", // This is the link to the next page
                "sLast": ">" // This is the link to the last page
            }
        },
        "scrollX": true,
        "initComplete": function (settings, json) {
        }
    });
    $(".check_all").on('change', function (e) {
        var $this = $(this);
        if ($this.is(':checked') === true) {
            $this.parents('div#individualcolumn_wrapper').find('[type="checkbox"]').prop('checked', true);
        }
        else {
            $this.parents('div#individualcolumn_wrapper').find('[type="checkbox"]').prop('checked', false);
        }
    });
    /*$('.mail_message .checkbox').change(function () {
     var $this = $(this),
     $checkvalue = $this.find('[type="checkbox"]');
     $checkvalue.is(":checked") ? $checkvalue.parents('label').addClass("checked") : $checkvalue.parents('label').removeClass("checked");
     $this.find('[type="checkbox"]').length == $this.find('[type="checkbox"]:checked').length ? $this.closest('table').closest('.dataTables_scroll').find(".check_all").children('label').addClass('checked').find('input[type="checkbox"]').prop('checked', true) : $this.closest('table').closest('.dataTables_scroll').find(".check_all").children('label').removeClass('checked').prop('checked', false);
     });*/

    // Filter
    $(".openUserlist").on('click', function () {

        $(".overlay-userlistNav").addClass("open-userlist-section");
    });
    $(".closeUserlist").on('click', function () {

        $(".overlay-userlistNav").removeClass("open-userlist-section");
    });

    // Apply the search
    individualcolumn.columns().every(function () {
        var that = this;

        $('input', this.footer()).on('keyup change', function () {
            if (that.search() !== this.value) {
                that
                    .search(this.value)
                    .draw();
            }
        });
    });
});