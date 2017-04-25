!function (document, window, $) {
    "use strict";
    var table1 = $('#eventdatatable').DataTable({
        "oLanguage": {
            "oPaginate": {
                "sFirst": "<", // This is the link to the first page
                "sPrevious": "«", // This is the link to the previous page
                "sNext": "»", // This is the link to the next page
                "sLast": ">" // This is the link to the last page
            }
        },
        "scrollX": true,
        "bAutoWidth": false,
        "scrollY": 380
    });
    $('#eventdatatable tbody').on('click', 'tr', function () {
        var data = table1.row(this).data();
        alert('You clicked on ' + data[0] + '\'s row');
    });

    var t = $('#addrowdatatable').DataTable({
        "oLanguage": {
            "oPaginate": {
                "sFirst": "<", // This is the link to the first page
                "sPrevious": "«", // This is the link to the previous page
                "sNext": "»", // This is the link to the next page
                "sLast": ">" // This is the link to the last page
            }
        },
        "bAutoWidth": false,
        "scrollX": true
    });
    var counter = 1;

    $('#addRow').on('click', function () {
        t.row.add([
            counter + '.1',
            counter + '.2',
            counter + '.3',
            counter + '.4',
            counter + '.5'
        ]).draw(false);

        counter++;
    });

    // Automatically add a first row of data
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
        "bAutoWidth": false,
        "scrollX": true
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

    $('#multi-table').DataTable({
        "columnDefs": [{
            targets: [0],
            orderData: [0, 1]
        }, {
            targets: [1],
            orderData: [1, 0]
        }, {
            targets: [4],
            orderData: [4, 0]
        }],
        "oLanguage": {
            "oPaginate": {
                "sFirst": "<", // This is the link to the first page
                "sPrevious": "«", // This is the link to the previous page
                "sNext": "»", // This is the link to the next page
                "sLast": ">" // This is the link to the last page
            }
        },
        "bAutoWidth": false,
        "scrollX": true
    });

    $('#editable-table').editableTableWidget();

    CORE_TEMP.function.initPerfectScroll($(".dataTables_scrollBody"));

}(document, window, jQuery);
