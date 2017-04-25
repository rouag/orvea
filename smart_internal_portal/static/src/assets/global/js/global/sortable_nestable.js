!function (document, window, $) {
    "use strict";
    $('#nestable-menu').on('click', function(e)
    {
        var target = $(e.target),
            action = target.data('action');
        if (action === 'expand-all') {
            $('.nestable-collapse').nestable('expandAll');
        }
        if (action === 'collapse-all') {
            $('.nestable-collapse').nestable('collapseAll');
        }
    });

    var editableList = Sortable.create(editable, {
        animation: 150,
        filter: '.js-remove',
        onFilter: function (evt) {
            evt.item.parentNode.removeChild(evt.item);
        }
    });
    $('#save-list').on('click',function () {
        console.log("Adj");
        var name = $("#list-content").val();
        if($("#list-content").val() == "" )
        {
            alert("Please Enter some text");
        }
        else{
            $("#editable").prepend('<li><span class="js-remove float-xs-right"><i class="icon_close "></i></span>' + name + '</li>');
            $("#addlist").modal('hide');
        }
    });
    $('.add-list-btn').on('click', function() {
        var $form = $('#list-form');
        $form[0].reset();
        $form.find('input, select, textarea').change();
    });
}(document, window, jQuery);

