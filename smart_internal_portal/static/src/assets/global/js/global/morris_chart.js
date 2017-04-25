!function (document, window, $) {
    "use strict";

    /*---- Line chart ----*/
    var line = Morris.Line({
        element: 'line-chart',
        data: [
            {y: '2006', a: 25, b: 90},
            {y: '2007', a: 35, b: 25},
            {y: '2008', a: 30, b: 95},
            {y: '2009', a: 85, b: 0},
            {y: '2010', a: 60, b: 50},
            {y: '2011', a: 55, b: 15},
            {y: '2012', a: 20, b: 95},
            {y: '2013', a: 10, b: 0},
            {y: '2014', a: 10, b: 100},
            {y: '2015', a: 75, b: 40},
            {y: '2016', a: 65, b: 50}
        ],
        xkey: 'y',
        ykeys: ['a', 'b'],
        lineColors: ['#088079', '#c9302c'],
        labels: ['A', 'B'],
        resize: true,
        stack: true,
        redraw: true
    });


    /*---- Area chart ----*/
    var area = Morris.Area({
        element: 'area-chart',
        data: [
            {y: '2009', a: 100, b: 100},
            {y: '2010', a: 100, b: -25},
            {y: '2011', a: 40, b: 40},
            {y: '2012', a: 65, b: -15},
            {y: '2013', a: 50, b: 10},
            {y: '2014', a: 35, b: 65},
            {y: '2015', a: 100, b: -20},
            {y: '2016', a: 60, b: 100}
        ],
        xkey: 'y',
        ykeys: ['a', 'b'],
        lineColors: ['#088079', '#c9302c'],
        fillOpacity: 0.6,
        labels: ['A', 'B'],
        resize: true,
        stack: true,
        redraw: true
    });


    /*---- Decimal data ----*/
    for (var a = [], b = 0; 360 >= b; b += 10) a.push({
        x: b,
        y: 4 * Math.sin(Math.PI * b / 180).toFixed(4)
    });

    var decimal = Morris.Line({
        element: "decimal-data",
        data: a,
        xkey: "x",
        ykeys: ["y"],
        labels: ["sin(x)"],
        parseTime: !1,
        lineColors: ['#088079'],
        resize: true,
        stack: true,
        redraw: true

    });

    /*---- Bars color ----*/
    var barscolor = Morris.Bar({
            element: 'bars-color',
            data: [
                {x: '2015 Q1', y: 1},
                {x: '2015 Q2', y: 2},
                {x: '2015 Q3', y: 3},
                {x: '2015 Q4', y: 4},
                {x: '2016 Q1', y: 5},
                {x: '2016 Q2', y: 6},
                {x: '2016 Q3', y: 7},
                {x: '2016 Q4', y: 7.5},
                {x: '2017 Q1', y: 8}
            ],
            xkey: 'x',
            ykeys: ['y'],
            labels: ['Y'],
            resize: true,
            stack: true,
            redraw: true,
            barColors: function (row, series, type) {
                if (type === 'bar') {
                    var green = Math.ceil(70 * row.y / this.ymax);
                    return 'rgb(' + green + ',115,128)';
                }
                else {
                    return '#000';
                }
            }
        });

    /*---- Bars charts ----*/
    var bar = Morris.Bar({
        element: 'bar-charts',
        data: [
            {x: '2016 Q1', y: 4, z: 1, a: 2},
            {x: '2016 Q2', y: 3, z: 4, a: null},
            {x: '2016 Q3', y: 2, z: 3, a: 4},
            {x: '2016 Q4', y: 1, z: 3, a: 2}
        ],
        xkey: 'x',
        ykeys: ['y', 'z', 'a'],
        labels: ['Y', 'Z', 'A'],
        barColors: ['#088079', '#c9302c', '#ec971f'],
        resize: true,
        stack: true,
        redraw: true
    });

    /*---- Stacked charts ----*/
    var stacked = Morris.Bar({
        element: 'stacked-charts',
        stacked: true,
        redraw: true,
        data: [
            {x: '2016 Q1', y: 4, z: 1, a: 2},
            {x: '2016 Q2', y: 3, z: 4, a: null},
            {x: '2016 Q3', y: 2, z: 3, a: 4},
            {x: '2016 Q4', y: 1, z: 3, a: 2}
        ],
        xkey: 'x',
        ykeys: ['y', 'z', 'a'],
        labels: ['Y', 'Z', 'A'],
        barColors: ['#088079', '#c9302c', '#ec971f'],
        resize: true,
        stack: true
    });

    /*---- Months bars ----*/
    var month = Morris.Bar({
        element: 'month-bars',
        data: [
            {x: 'Jan', y: 4},
            {x: 'Feb', y: 3},
            {x: 'Mar', y: 2},
            {x: 'Apr', y: 1},
            {x: 'May', y: 2},
            {x: 'June', y: 3},
            {x: 'July', y: 1},
            {x: 'Aug', y: 2},
            {x: 'Sep', y: 4},
            {x: 'Oct', y: 2},
            {x: 'Nov', y: 3},
            {x: 'Dec', y: 1}
        ],
        xkey: 'x',
        ykeys: ['y'],
        labels: ['Y'],
        xLabelAngle: 86,
        hideHover: "auto",
        barColors: ['#088079'],
        resize: true,
        stack: true,
        redraw: true
    });

    /*---- Negative bars ----*/
    var neg_data = [
        {"period": "2017-08-12", "a": 100},
        {"period": "2017-03-03", "a": 50},
        {"period": "2010-08-08", "a": 75},
        {"period": "2010-05-10", "a": 25},
        {"period": "2010-03-14", "a": 0},
        {"period": "2010-01-10", "a": -25},
        {"period": "2009-12-10", "a": -75},
        {"period": "2009-10-07", "a": -50},
        {"period": "2009-09-25", "a": -100}
    ];

    var negative = Morris.Line({
        element: 'negative-charts',
        data: neg_data,
        xkey: 'period',
        ykeys: ['a'],
        labels: ['Series A'],
        units: '%',
        lineColors: ['#088079'],
        resize: true,
        stack: true,
        redraw: true
    });

    /*---- Labels Diagonally ----*/
    var day_data = [
        {"period": "2012-10-30", "licensed": 3407, "sorned": 660},
        {"period": "2012-09-30", "licensed": 3351, "sorned": 629},
        {"period": "2012-09-29", "licensed": 3269, "sorned": 618},
        {"period": "2012-09-20", "licensed": 3246, "sorned": 661},
        {"period": "2012-09-19", "licensed": 3257, "sorned": 667},
        {"period": "2012-09-18", "licensed": 3248, "sorned": 627},
        {"period": "2012-09-17", "licensed": 3171, "sorned": 660},
        {"period": "2012-09-16", "licensed": 3171, "sorned": 676},
        {"period": "2012-09-15", "licensed": 3201, "sorned": 656},
        {"period": "2012-09-10", "licensed": 3215, "sorned": 622}
    ];
    var labels = Morris.Line({
        element: 'labels-diagonally',
        data: day_data,
        xkey: 'period',
        ykeys: ['licensed', 'sorned'],
        labels: ['Licensed', 'SORN'],
        lineColors: ['#088079', '#c9302c'],
        xLabelAngle: 60,
        resize: true,
        stack: true,
        redraw: true
    });

    /*---- Non-continuous data ----*/
    var day_data = [
        {"period": "2012-10-01", "licensed": 3407},
        {"period": "2012-09-30", "sorned": 0},
        {"period": "2012-09-29", "sorned": 618},
        {"period": "2012-09-20", "licensed": 3246, "sorned": 661},
        {"period": "2012-09-19", "licensed": 3957, "sorned": null},
        {"period": "2012-09-18", "licensed": 3248, "other": 2000},
        {"period": "2012-09-17", "sorned": 650},
        {"period": "2012-09-16", "sorned": 0},
        {"period": "2012-09-15", "licensed": 3201, "sorned": 650},
        {"period": "2012-09-12", "sorned": 650},
        {"period": "2012-09-10", "licensed": 3215}
    ];

    var noncontinuous = Morris.Line({
        element: 'non-continuous-data',
        data: day_data,
        xkey: 'period',
        ykeys: ['licensed', 'sorned', 'other'],
        labels: ['Licensed', 'SORN', 'Other'],
        lineColors: ['#088079', '#c9302c'],
        xLabelFormat: function (d) {
            return (d.getMonth() + 1) + '/' + d.getDate() + '/' + d.getFullYear();
        },
        xLabels: 'day',
        resize: true,
        stack: true,
        redraw: true
    });

    /*---- Time events ----*/
    var week_data = [
        {"period": "2017 W27", "licensed": 3400, "sorned": 650},
        {"period": "2017 W26", "licensed": 3300, "sorned": 850},
        {"period": "2017 W25", "licensed": 2900, "sorned": 200},
        {"period": "2017 W24", "licensed": 2800, "sorned": 660},
        {"period": "2017 W23", "licensed": 2700, "sorned": 660},
        {"period": "2017 W22", "licensed": 2750, "sorned": 627},
        {"period": "2017 W21", "licensed": 2800, "sorned": 660},
        {"period": "2017 W20", "licensed": 2900, "sorned": 676},
        {"period": "2017 W19", "licensed": 2950, "sorned": 656},
        {"period": "2017 W18", "licensed": 3000, "sorned": 622},
        {"period": "2017 W17", "licensed": 3100, "sorned": 632},
        {"period": "2017 W16", "licensed": 3200, "sorned": 681},
        {"period": "2017 W15", "licensed": 3250, "sorned": 667},
        {"period": "2017 W14", "licensed": 3300, "sorned": 620},
        {"period": "2017 W13", "licensed": 3400, "sorned": null},
        {"period": "2017 W12", "licensed": 3350, "sorned": null},
        {"period": "2017 W11", "licensed": 3300, "sorned": null},
        {"period": "2017 W10", "licensed": 3200, "sorned": null},
        {"period": "2017 W09", "licensed": 2950, "sorned": null},
        {"period": "2017 W08", "licensed": 2900, "sorned": null},
        {"period": "2017 W07", "licensed": 3000, "sorned": null},
        {"period": "2017 W06", "licensed": 3050, "sorned": null},
        {"period": "2017 W05", "licensed": 2900, "sorned": null},
        {"period": "2017 W04", "licensed": 2800, "sorned": null},
        {"period": "2017 W03", "licensed": 2500, "sorned": null},
        {"period": "2017 W02", "licensed": 1600, "sorned": null},
        {"period": "2017 W01", "licensed": 1500, "sorned": null}
    ];
    var timeevent = Morris.Line({
        element: 'time-events',
        data: week_data,
        xkey: 'period',
        ykeys: ['licensed', 'sorned'],
        labels: ['Licensed', 'SORN'],
        lineColors: ['#088079', '#c9302c'],
        events: [
            '2017-04',
            '2017-08'
        ],
        resize: true,
        stack: true,
        redraw: true
    });

    /*---- Donut chart ----*/
    var donut = Morris.Donut({
        element: 'donut-chart',
        data: [
            {value: 50, label: 'sam'},
            {value: 20, label: 'Europan'},
            {value: 30, label: 'nov'}
        ],
        labelColor: ['#088079'],
        colors: ['#088079', '#327380', '#4B7380'],
        resize: true,
        redraw: true,
        stack: true,
        formatter: function (x) {
            return x + "%"
        }
    }).on('click', function (i, row) {
        console.log(i, row);
    });

    /*---- Donut color ----*/
    var donutcolor = Morris.Donut({
        element: 'donut-color',
        data: [
            {value: 20, label: 'Php'},
            {value: 30, label: 'Css'},
            {value: 15, label: 'jQuery'},
            {value: 35, label: 'HTML'}
        ],
        backgroundColor: '#ccc',
        labelColor: '#088079',
        colors: ['#088079', '#1E8693', '#329BA8', '#4EB9C6'],
        resize: true,
        redraw: true,
        stack: true,
        formatter: function (x) {
            return x + "%"
        }
    });

    /*---- Donut formatter ----*/
    var donutformate = Morris.Donut({
        element: 'donut-formatter',
        data: [
            {value: 35, label: 'Mozilla', formatted: 'at uniform 35%'},
            {value: 25, label: 'Chrome', formatted: 'lingue. 25%'},
            {value: 20, label: 'Safari', formatted: 'simplic 20%'},
            {value: 15, label: 'Opera', formatted: 'at esser 15%'},
            {value: 5, label:  'IE', formatted: 'lingue. 5%'}
        ],
        labelColor: ['#088079'],
        colors: ['#088079', '#1E8693', '#329BA8', '#4EB9C6'],
        resize: true,
        redraw: true,
        stack: true,
        formatter: function (x, data) {
            return data.formatted;
        }
    });

    /*Morris.redraw();
     $(window).on('resize', function() {
     if (!window.recentResize) {
     window.m.redraw();
     window.recentResize = true;
     setTimeout(function(){ window.recentResize = false; }, 200);
     }
     });*/

    var resizeEnd;
    $(window).on('resize', function() {
        clearTimeout(resizeEnd);
        resizeEnd = setTimeout(function() {
            $(window).trigger('resize-end');
        }, 2500);
    });

    $(window).on('resize-end', function() {
        line.redraw();
        area.redraw();
        decimal.redraw();
        barscolor.redraw();
        bar.redraw();
        stacked.redraw();
        month.redraw();
        negative.redraw();
        labels.redraw();
        noncontinuous.redraw();
        timeevent.redraw();
        donut.redraw();
        donutcolor.redraw();
        donutformate.redraw();
    });

}(document, window, jQuery);