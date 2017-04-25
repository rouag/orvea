!function (document, window, $) {
    "use strict";
    var map2, infoWindow;
    var coordinates2 = {
        lat: -12.043333,
        lng: -77.028333
    };
    map2 = new GMaps({
        el: '#Markets-map',
        lat: coordinates2.lat,
        lng: coordinates2.lng,
        resize: function () {
            this.setCenter(coordinates2);
        },
        tilesloaded: function () {
            map2.refresh();
        }
    });
    map2.addMarker({
        lat: -12.043333,
        lng: -77.03,
        title: 'Lima',
        details: {
            database_id: 42,
            author: 'HPNeo'
        },
        click: function (e) {
            if (console.log)
                console.log(e);
            alert('You clicked in this marker');
        },
        mouseover: function (e) {
            if (console.log)
                console.log(e);
        }
    });
    map2.addMarker({
        lat: -12.042,
        lng: -77.028333,
        title: 'Marker with InfoWindow',
        infoWindow: {
            content: '<p>HTML Content</p>'
        }
    });
}(document, window, jQuery);
