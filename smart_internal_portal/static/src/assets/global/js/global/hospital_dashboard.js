!function (document, window, $) {
    "use strict";
    /*---- Bar chart ----*/
    $(".stackline-bar").sparkline("html", {
        type: "bar",
        height: "50px",
        barWidth: 10,
        barSpacing: 5,
        barColor: ['#088079'],
        negBarColor: ['#c9302c'],
        stackedBarColor: ['#088079', "#c9302c"]
    });

    /*---- Line chart ----*/
    $(".sparkline-line").sparkline("html", {
        height: "50px",
        width: "100px",
        lineColor: ['#449d44'],
        fillColor: ['transparent']
    });

    /*---- inline range chart ----*/
    $(".sparkline-inlinerange").sparkline("html", {
        fillColor: !1,
        height: "50px",
        width: "100px",
        lineColor: ['#c9302c'],
        spotColor: ['#088079'],
        minSpotColor: ['#088079'],
        maxSpotColor: ['#088079'],
        normalRangeColor: ['transparent'],
        normalRangeMin: -1,
        normalRangeMax: 8
    });

    /*---- line custom chart ----*/
    $(".sparkline-linecustom").sparkline("html", {
        height: "50px",
        width: "100px",
        lineColor: ['#f0ad4e'],
        fillColor: ['transparent'],
        minSpotColor: !1,
        maxSpotColor: !1,
        spotColor: ['green'],
        spotRadius: 2
    });

    /*---- Carousel ----*/
    $("#owl-full").owlCarousel({
        navigation: true,
        slideSpeed: 400,
        loop: true,
        autoplay: true,
        dots: false,
        autoplayTimeout: 3000,
        autoplayHoverPause: true,
        paginationSpeed: 500,
        items: 1,
    });

    $(function () {
        // We use an inline data source in the example, usually data would
        // be fetched from a server
        var data = [], totalPoints = 300;

        function getRandomData() {
            if (data.length > 0)
                data = data.slice(1);

            while (data.length < totalPoints) {
                var prev = data.length > 0 ? data[data.length - 1] : 50,
                    y = prev + Math.random() * 10 - 5;
                if (y < 0) {
                    y = 0;
                } else if (y > 100) {
                    y = 100;
                }
                data.push(y);
            }

            var res = [];
            for (var i = 0; i < data.length; ++i) {
                res.push([i, data[i]])
            }
            return res;
        }

        // Set up the control widget
        var updateInterval = 50;
        var plot = $.plot("#liveoperations", [getRandomData()], {
            series: {
                shadowSize: 0	// Drawing is faster without shadows
            },
            grid: {borderWidth: 0, labelMargin: 0, axisMargin: 0, minBorderMargin: 0},
            yaxis: {
                min: 0,
                max: 100
            },
            xaxis: {
                show: false
            },
            colors: ["#088079"]
        });

        function update() {
            plot.setData([getRandomData()]);
            // Since the axes don't change, we don't need to call plot.setupGrid()
            plot.draw();
            setTimeout(update, updateInterval);
        }

        update();
    });

    /*---- Donut-color ----*/
    var donut = Morris.Donut({
        element: 'donut-color',
        data: [
            {value: 40, label: 'Satisfied'},
            {value: 35, label: 'Neutral'},
            {value: 25, label: 'Unsetisfied'}
        ],
        backgroundColor: '#ccc',
        labelColor: '#449d44',
        colors: ['#449d44', '#c9302c', '#ec971f'],
        resize: true,
        formatter: function (x) {
            return x + "%"
        }
    });



    var myChart1 = echarts.init(document.getElementById('multipal-funnels'));
    myChart1.setOption({
        color: [
            '#F2784B',
            '#088079',
            '#ec407a',
            '#eb6d6d',
            '#6d5cae'
        ],
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c}%"
        },
        resize: true,
        toolbox: {
            show: true,
            feature: {
                mark: {show: false},
                dataView: {show: false, readOnly: false},
                restore: {show: false},
                saveAsImage: {show: false}
            }
        },
        legend: {
            data: ['aa', 'bb', 'cc', 'dd', 'ee'],
            show: false
        },
        hoverLink: false,
        calculable: true,
        series: [
            {
                name: 'expected',
                type: 'funnel',
                sort: 'ascending',
                x: '10%',
                width: '80%',
                itemStyle: {
                    normal: {
                        label: {
                            formatter: '{b}'
                        },
                        labelLine: {
                            show: false
                        }
                    },
                    emphasis: {
                        label: {
                            position: 'inside',
                            formatter: '{b} : {c}%',
                            show: false
                        }
                    }
                },
                data: [
                    {value: 100, name: '2012'},
                    {value: 80, name: '2013'},
                    {value: 40, name: '2015'},
                    {value: 20, name: '2016'},
                    {value: 60, name: '2014'}
                ]
            },
            {
                name: 'actual',
                type: 'funnel',
                x: '10%',
                sort: 'ascending',
                width: '80%',
                maxSize: '80%',
                itemStyle: {
                    normal: {
                        borderColor: '#fff',
                        borderWidth: 2,
                        label: {
                            position: 'inside',
                            formatter: '{c}%',
                            textStyle: {
                                color: '#fff'
                            }
                        }
                    },
                    emphasis: {
                        label: {
                            position: 'inside',
                            formatter: '{b} : {c}%',
                        }
                    }
                },
                data: [
                    {value: 80, name: '2012'},
                    {value: 50, name: '2013'},
                    {value: 5, name: '2015'},
                    {value: 10, name: '2016'},
                    {value: 30, name: '2014'}
                ]
            }
        ]

    });

    var myChart2 = echarts.init(document.getElementById('angular-gauge'));
    myChart2.setOption({
        tooltip : {
            formatter: "{a} <br/>{b} : {c}%"
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: false},
                restore : {show: false},
                saveAsImage : {show: false}
            }
        },
        series : [
            {
                name:'Attention',
                type:'gauge',
                detail : {formatter:'{value}%'},
                data:[{value: 43, name: 'Patients'}]
            }
        ]
    });

    function escapeXml(string) {
        return string.replace(/[<>]/g, function (c) {
            switch (c) {
                case '<':
                    return '\u003c';
                case '>':
                    return '\u003e';
            }
        });
    }

    var pins = {
        mo: escapeXml('<div class="map-pin red"><span>MO</span></div>'),
        fl: escapeXml('<div class="map-pin blue"><span>FL</span></div>'),
        or: escapeXml('<div class="map-pin purple"><span>OR</span></div>')
    };


    function chartistChart() {

        /*---- simple line chart ----*/
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

        /*---- google map ----*/
        var map6 = new GMaps({
            el: '#Overlays-map',
            lat: -12.043333,
            lng: -77.028333
        });
        map6.drawOverlay({
            lat: map6.getCenter().lat(),
            lng: map6.getCenter().lng(),
            layer: 'overlayLayer',
            content: '<div class="overlay-map">Hospital<div class="overlay_arrow-map above"></div></div>',
            verticalAlign: 'top',
            horizontalAlign: 'center'
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


    window.onresize = function () {
        myChart1.resize();
        myChart2.resize();
    }

}(document, window, jQuery);
