!function (document, window, $) {
    "use strict";
    new SimpleMDE({
        element: document.getElementById("autosave"),
        spellChecker: false,
        autosave: {
            enabled: true
        }
    });

    var simplemde = new SimpleMDE({
        element: document.getElementById("custom"),
        toolbar: [{
            name: "font-bold",
            action: exampleAction,
            className: "fa fa-bolt",
            title: "font-bold",
        },
            {
                name: "font-italic",
                action: exampleAction,
                className: "fa fa-italic",
                title: "font-italic",
            }
        ],
    });

    function exampleAction(e) {
        console.log(e);
        alert("Custom toolbar clicked");
    }
}(document, window, jQuery);
