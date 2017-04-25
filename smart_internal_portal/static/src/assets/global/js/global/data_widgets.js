!function (document, window, $) {
    "use strict";
    $("#owl-full").owlCarousel({
        navigation: true,
        slideSpeed: 400,
        paginationSpeed: 500,
        items: 1,
    });
    $('#world-map').vectorMap({
        map: 'world_en',
        color: '#ffffff',
        hoverOpacity: 0.7,
        backgroundColor: '#eaeaea',
        selectedColor: '#088079',
        borderOpacity: 0.25,
        borderColor:'#fff',
        enableZoom: true,
        showTooltip: true,
        values: sample_data,
        scaleColors: ['#C8EEFF', '#088079'],
        normalizeFunction: 'polynomial'
    });

    /*---- Area chart ----*/
    Morris.Area({
        element: 'area-chart',
        data: [
            { y: '2009', a: 100, b: 100 },
            { y: '2010', a: 100,  b: -25 },
            { y: '2011', a: 40,  b: 40 },
            { y: '2012', a: 65,  b: -15 },
            { y: '2013', a: 50,  b: 10 },
            { y: '2014', a: 35,  b: 65 },
            { y: '2015', a: 100,  b: -20 },
            { y: '2016', a: 60,  b: 100 }
        ],
        xkey: 'y',
        ykeys: ['a', 'b'],
        lineColors: ['#088079', '#c9302c'],
        fillOpacity: 0.6,
        labels: ['A', 'B'],
        resize: true
    });

}(document, window, jQuery);
