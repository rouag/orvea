$(function () {
    "use strict";
    $('#addRow').click();

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
    });

    // Filter
    $(".openUserlist").on('click',function () {

        $(".overlay-userlistNav").addClass("open-userlist-section");
    });
    $(".closeUserlist").on('click',function () {

        $(".overlay-userlistNav").removeClass("open-userlist-section");
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

    function format(d) {
        // `d` is the original data object for the row
        return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
            '<tr>' +
            '<td>Full name:</td>' +
            '<td>' + d.name + '</td>' +
            '</tr>' +
            '<tr>' +
            '<td>Extension number:</td>' +
            '<td>' + d.extn + '</td>' +
            '</tr>' +
            '<tr>' +
            '<td>Extra info:</td>' +
            '<td>And any further details here (images etc)...</td>' +
            '</tr>' +
            '</table>';
    }


    var table = $('#childrowdata').DataTable({
        "ajax": "../../..//smart_internal_portal/static/src/assets/data/childrow.txt",
        "columns": [
            {
                "className": 'details-control icon_plus_alt2 text-xs-center',
                "orderable": false,
                "data": null,
                "defaultContent": ''
            },
            {"data": "name"},
            {"data": "position"},
            {"data": "office"},
            {"data": "salary"}
        ],
        "oLanguage": {
            "oPaginate": {
                "sFirst": "<", // This is the link to the first page
                "sPrevious": "«", // This is the link to the previous page
                "sNext": "»", // This is the link to the next page
                "sLast": ">" // This is the link to the last page
            }
        },
        "order": [[1, 'asc']]
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


});