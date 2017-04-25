!function (document, window, $) {
    "use strict";
    var drEvent = $('#input-file-events').dropify({
        'height':'365'
    });

    drEvent.on('dropify.beforeClear', function (event, element) {
        return confirm("Do you really want to delete \"" + element.file.name + "\" ?");
    });

    drEvent.on('dropify.afterClear', function (event, element) {
        alert('File deleted');
    });

    drEvent.on('dropify.errors', function (event, element) {
        console.log('Has Errors');
    });
}(document, window, jQuery);
