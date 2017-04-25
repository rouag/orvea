!function (document, window, $) {
    "use strict";


    // Make some random data for the Chart
    var d1 = [];
    for (var i = 0; i <= 10; i += 1) {
        d1.push([i, parseInt(Math.random() * 30)]);
    }
    var d2 = [];
    for (var i = 0; i <= 25; i += 4) {
        d2.push([i, parseInt(Math.random() * 30)]);
    }
    var d3 = [];
    for (var i = 0; i <= 10; i += 1) {
        d3.push([i, parseInt(Math.random() * 30)]);
    }

    // Chart Options
    var options = {
        series: {
            shadowSize: 0,
            curvedLines: {
                apply: true,
                active: true,
                monotonicFit: true
            },
            lines: {
                show: false,
                lineWidth: 0
            }
        },
        grid: {
            borderWidth: 0,
            labelMargin:10,
            hoverable: true,
            clickable: true,
            mouseActiveRadius:6

        },
        xaxis: {
            tickDecimals: 0,
            ticks: false
        },

        yaxis: {
            tickDecimals: 0,
            ticks: false
        },

        legend: {
            show: false
        }
    };

    // Let's create the chart
    if ($("#chart-curved-line")[0]) {
        $.plot($("#chart-curved-line"), [
            {
                data: d1,
                lines: {
                    show: true,
                    fill: true
                },
                label: 'Item 1',
                stack: true,
                color: '#088079'
            }, {
                data: d3,
                lines: {
                    show: true,
                    fill: true
                },
                label: 'Item 2',
                stack: true,
                color: '#F3C200'
            }
        ], options);
    }

    if ($("#chart-past-days")[0]) {
        $.plot($("#chart-past-days"), [{
            data: d2,
            lines: {
                show: true,
                fill: 1,
            },
            label: 'Product 1',
            stack: true,
            color: '#35424b'
        }], options);
    }

    // Tooltips for Flot Charts
    if ($('.flot-chart')[0]) {
        $('.flot-chart').bind('plothover', function (event, pos, item) {
            if (item) {
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);
                $('.flot-tooltip').html(item.series.label + ' of ' + x + ' = ' + y).css({top: item.pageY+5, left: item.pageX+5}).show();
            }
            else {
                $('.flot-tooltip').hide();
            }
        });

        $('<div class="flot-tooltip"></div>').appendTo('body');
    }

    /*---- Bar chart ----*/
    $(".stackline-bar").sparkline("html", {
        type: "bar",
        height: "100px",
        barWidth: 10,
        barSpacing: 5,
        barColor: ['#088079'],
        negBarColor: ['#c9302c'],
        stackedBarColor: ['#088079', "#c9302c"]
    });

    $(".sparkline-pie").sparkline("html", {
        type: "pie",
        height: "100px",
        sliceColors: ['#088079', '#057b8a', '#069caf']
    });

    /*---- inline range chart ----*/
    $(".sparkline-inlinerange").sparkline("html", {
        fillColor: !1,
        height: "100px",
        width: "100px",
        lineColor: ['#088079'],
        spotColor: ['#00e3ff'],
        minSpotColor: ['#00e3ff'],
        maxSpotColor: ['#00e3ff'],
        normalRangeColor: ['transparent'],
        normalRangeMin: -1,
        normalRangeMax: 8
    });


    function chart_order_survey() {

        var d1 = [],
            series = Math.floor(Math.random() * 6) + 3;

        d1[0] = {
            label: "Success",
            data: Math.floor(Math.random() * 100) + 1
        };
        d1[1] = {
            label: "Pending",
            data: Math.floor(Math.random() * 100) + 1
        };
        d1[2] = {
            label: "Not available",
            data: Math.floor(Math.random() * 100) + 1
        };
        d1[3] = {
            label: "Progress",
            data: Math.floor(Math.random() * 100) + 1
        };
        d1[4] = {
            label: "Others",
            data: Math.floor(Math.random() * 100) + 1
        };
        $.plot('#order-chart', d1, {
            series : {
                pie : {
                    innerRadius : 0.4,
                    show : true,
                    stroke : {
                        width : 0
                    },
                    label : {
                        show : true,
                        threshold : 0.05
                    }
                }
            },
            colors : ['#15b315','#febf34','#ff4a5d','#F2784B','#363b5b'],
            grid : {
                hoverable : true
            }
        });
    }

    chart_order_survey();


    // var myChart = echarts.init(document.getElementById('basic-area'));
    // myChart.setOption({
    //     tooltip : {
    //         trigger: 'axis',
    //         axisPointer : {
    //             type : 'shadow'
    //         },
    //         formatter: function (params){
    //             return params[0].name + '<br/>'
    //                 + params[0].seriesName + ' : ' + params[0].value + '<br/>'
    //                 + params[1].seriesName + ' : ' + (params[1].value + params[0].value);
    //         }
    //     },
    //     resize: true,
    //     legend: {
    //         selectedMode:false,
    //         data:['Acutal', 'Forecast']
    //     },
    //     toolbox: {
    //         show : true,
    //         feature : {
    //             mark : {show: true},
    //             dataView : {show: false, readOnly: false},
    //             restore : {show: false},
    //             saveAsImage : {show: false}
    //         }
    //     },
    //     calculable: true,
    //     xAxis : [
    //         {
    //             type : 'category',
    //             data : ['Cosco','CMA','APL','OOCL','Wanhai','Zim']
    //         }
    //     ],
    //     yAxis : [
    //         {
    //             type : 'value',
    //             boundaryGap: [0, 0.1]
    //         }
    //     ],
    //     series : [
    //         {
    //             name:'Acutal',
    //             type:'bar',
    //             stack: 'sum',
    //             barCategoryGap: '50%',
    //             itemStyle: {
    //                 normal: {
    //                     color: '#088079',
    //                     barBorderColor: '#088079',
    //                     barBorderWidth: 6,
    //                     barBorderRadius:0,
    //                     label : {
    //                         show: true, position: 'insideTop'
    //                     }
    //                 }
    //             },
    //             data:[26, 20, 22, 12, 10, 8]
    //         },
    //         {
    //             name:'Forecast',
    //             type:'bar',
    //             stack: 'sum',
    //             itemStyle: {
    //                 normal: {
    //                     color: '#ccc',
    //                     barBorderColor: '#088079',
    //                     barBorderWidth: 6,
    //                     barBorderRadius:0,
    //                     label : {
    //                         show: true,
    //                         position: 'top',
    //                         textStyle: {
    //                             color: '#088079'
    //                         }
    //                     }
    //                 }
    //             },
    //             data:[4, 3, 5, 8 ,8 , 7]
    //         }
    //     ]
    //
    // });

    var myChart2 = echarts.init(document.getElementById('sales-data-chart'));
    myChart2.setOption({
        tooltip : {
            trigger: 'axis'
        },
        resize: true,
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataView : {show: false, readOnly: false},
                magicType : {show: false, type: ['line', 'bar']},
                restore : {show: false},
                saveAsImage : {show: false}
            }
        },
        legend: {
            data:['This week', 'Last week'],
            selectedMode:false
        },
        xAxis : [
            {
                type : 'category',
                data : ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            }
        ],
        yAxis : [
            {
                type : 'value',
                min : 200,
                max : 450
            }
        ],
        series : [
            {
                name:'This week',
                type:'line',
                data:[400, 374, 251, 300, 420, 400, 440]
            },
            {
                name:'Last week',
                type:'line',
                symbol:'none',
                itemStyle:{
                    normal:{
                        lineStyle: {
                            width:1,
                            type:'dashed'
                        }
                    }
                },
                data:[320, 332, 301, 334, 360, 330, 350]
            },
            {
                name:'Last week 2',
                type:'bar',
                stack: '1',
                barWidth: 6,
                itemStyle:{
                    normal:{
                        color:'rgba(0,0,0,0)'
                    },
                    emphasis:{
                        color:'rgba(0,0,0,0)'
                    }
                },
                data:[320, 332, 251, 300, 360, 330, 350]
            },
            {
                name:'Variety',
                type:'bar',
                stack: '1',
                data:[
                    80, 42,
                    {value : 50, itemStyle:{ normal:{color:'red'}}},
                    {value : 34, itemStyle:{ normal:{color:'red'}}},
                    60, 70, 90
                ]
            }
        ]

    });

    var myChart3 = echarts.init(document.getElementById('left-right-chart'));
    var labelRight = {normal: {label : {position: 'right'}}};
    myChart3.setOption({
        tooltip : {
            trigger: 'axis',
            axisPointer : {
                type : 'shadow'
            }
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: false},
                dataView : {show: false, readOnly: false},
                magicType : {show: false, type: ['line', 'bar']},
                restore : {show: false},
                saveAsImage : {show: false}
            }
        },
        grid: {
            y: 80,
            y2: 30
        },
        xAxis : [
            {
                type : 'value',
                position: 'top',
                splitLine: {lineStyle:{type:'dashed'}},
            }
        ],
        yAxis : [
            {
                type : 'category',
                axisLine: {show: false},
                axisLabel: {show: false},
                axisTick: {show: false},
                splitLine: {show: false},
                data : ['ten', 'nine', 'eight', 'seven', 'six', 'five', 'four', 'three', 'two', 'one']
            }
        ],
        series : [
            {
                name:'Living expenses',
                type:'bar',
                stack: 'Amount',
                itemStyle : { normal: {
                    color: 'orange',
                    borderRadius: 5,
                    label : {
                        show: true,
                        position: 'left',
                        formatter: '{b}'
                    }
                }},
                data:[
                    {value:-0.07, itemStyle:labelRight},
                    {value:-0.09, itemStyle:labelRight},
                    0.2, 0.44,
                    {value:-0.23, itemStyle:labelRight},
                    0.08,
                    {value:-0.17, itemStyle:labelRight},
                    0.47,
                    {value:-0.36, itemStyle:labelRight},
                    0.18
                ]
            }
        ]

    });

    var myChart4 = echarts.init(document.getElementById('straight-line-chart'));
    myChart4.setOption({
        tooltip : {
            trigger: 'axis',
            axisPointer : {
                type : 'shadow'
            }
        },
        resize: true,
        legend: {
            data:['Show','Mail','Order','Video','Search']
        },
        toolbox: {
            show : true,
            orient: 'vertical',
            x: 'right',
            y: 'center',
            feature : {
                mark : {show: true},
                dataView : {show: false, readOnly: false},
                magicType : {show: false, type: ['line', 'bar', 'stack', 'tiled']},
                restore : {show: false},
                saveAsImage : {show: false}
            }
        },
        calculable : true,
        xAxis : [
            {
                type : 'category',
                data : ['January','February','March']
            }
        ],
        yAxis : [
            {
                type : 'value'
            }
        ],
        series : [
            {
                name:'Show',
                type:'bar',
                data:[320, 332, 301]
            },
            {
                name:'Mail',
                type:'bar',
                stack: 'advertising',
                data:[120, 132, 101]
            },
            {
                name:'Order',
                type:'bar',
                stack: 'advertising',
                data:[220, 182, 191]
            },
            {
                name:'Video',
                type:'bar',
                stack: 'advertising',
                data:[150, 232, 201]
            },
            {
                name:'Search',
                type:'bar',
                data:[862, 1018, 1679],
                markLine : {
                    itemStyle:{
                        normal:{
                            lineStyle:{
                                type: 'dashed'
                            }
                        }
                    },
                    data : [
                        [{type : 'min'}, {type : 'max'}]
                    ]
                }
            }
        ]

    });

    var myChart5 = echarts.init(document.getElementById('purely-chart'));
    myChart5.setOption({
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c}%"
        },
        resize: true,
        toolbox: {
            show : true,
            orient: 'vertical',
            y: 'center',
            feature : {
                mark : {show: false},
                dataView : {show: false, readOnly: false},
                restore : {show: false},
                saveAsImage : {show: false}
            }
        },
        legend: {
            orient: 'vertical',
            x: 'left',
            data : ['Show','Click','access','advisory','Order'],
            show: false
        },
        calculable : true,
        series : [
            {
                name:'Funnel',
                type:'funnel',
                width: '80%',
                height: '45%',
                x:'5%',
                y: '5%',
                itemStyle: {
                    normal: {
                        label: {
                            position: 'center'
                        }
                    }
                },
                data:[
                    {value:60, name:'access'},
                    {value:30, name:'advisory'},
                    {value:10, name:'Order'},
                    {value:80, name:'Click'},
                    {value:100, name:'Show'}
                ]
            },
            {
                name:'pyramid',
                type:'funnel',
                width: '80%',
                height: '45%',
                x:'5%',
                y:'50%',
                sort : 'ascending',
                itemStyle: {
                    normal: {
                        label: {
                            position: 'center'
                        }
                    }
                },
                data:[
                    {value:60, name:'access'},
                    {value:30, name:'advisory'},
                    {value:10, name:'Order'},
                    {value:80, name:'Click'},
                    {value:100, name:'Show'}
                ]
            }
        ]

    });

    var myChart6 = echarts.init(document.getElementById('axis-chart'));
    myChart6.setOption({
        tooltip : {
            trigger: 'axis',
            showDelay : 0,
            axisPointer:{
                show: true,
                type : 'cross',
                lineStyle: {
                    type : 'dashed',
                    width : 1
                }
            }
        },
        legend: {
            data:['sin','cos'],
            show: false
        },
        toolbox: {
            show : false,
            feature : {
                mark : {show: false},
                dataZoom : {show: false},
                dataView : {show: false, readOnly: false},
                restore : {show: false},
                saveAsImage : {show: false}
            }
        },
        xAxis : [
            {
                type : 'value',
                scale:true
            }
        ],
        yAxis : [
            {
                type : 'value',
                scale:true
            }
        ],
        series : [
            {
                name:'sin',
                type:'scatter',
                large: true,
                data: (function () {
                    var d = [];
                    var len = 1000;
                    var x = 0;
                    while (len--) {
                        x = (Math.random() * 10).toFixed(3) - 0;
                        d.push([
                            x,
                            //Math.random() * 10
                            (Math.sin(x) - x * (len % 2 ? 0.1 : -0.1) * Math.random()).toFixed(3) - 0
                        ]);
                    }
                    //console.log(d)
                    return d;
                })()
            },
            {
                name:'cos',
                type:'scatter',
                large: true,
                data: (function () {
                    var d = [];
                    var len = 1000;
                    var x = 0;
                    while (len--) {
                        x = (Math.random() * 10).toFixed(3) - 0;
                        d.push([
                            x,
                            //Math.random() * 10
                            (Math.cos(x) - x * (len % 2 ? 0.1 : -0.1) * Math.random()).toFixed(3) - 0
                        ]);
                    }
                    //console.log(d)
                    return d;
                })()
            }
        ]

    });

    window.onresize = function () {
        //myChart.resize();
        myChart2.resize();
        myChart3.resize();
        myChart4.resize();
        myChart5.resize();
        myChart6.resize();
    }
}(document, window, jQuery);
