!function (document, window, $) {
    "use strict";

    /*---- Line chart ----*/
    $(".sparkline-line").sparkline("html", {
        height: "200px",
        width: "200px",
        lineColor: ['#449d44'],
        fillColor: ['#82ce82']
    });

    /*---- Bar chart ----*/
    $(".stackline-bar").sparkline("html", {
        type: "bar",
        height: "200px",
        barWidth: 10,
        barSpacing: 5,
        barColor: ['#088079'],
        negBarColor: ['#c9302c'],
        stackedBarColor: ['#088079', "#c9302c"]
    });

    /*---- composite line chart ----*/
    $(".sparkline-compositeline").sparkline("html", {
        height: "200px",
        width: "200px",
        fillColor: !1,
        lineColor: ['#36a9e1'],
        spotColor: ['#5cb85c'],
        minSpotColor: ['#31b0d5'],
        maxSpotColor: ['#5cb85c'],
        changeRangeMin: 0,
        chartRangeMax: 10
    });

    $(".sparkline-compositeline").sparkline([3, 2, 4, 5, 7, 6, 7, 5, 5, 3, 6, 2, 8, 4, 2, 3, 5, 6], {
        composite: !0,
        fillColor: !1,
        height: "200px",
        width: "200px",
        lineColor: ['#c9302c'],
        spotColor: ['#5cb85c'],
        minSpotColor: ['#31b0d5'],
        maxSpotColor: ['#5cb85c'],
        changeRangeMin: 0,
        chartRangeMax: 10
    });

    /*---- inline range chart ----*/
    $(".sparkline-inlinerange").sparkline("html", {
        fillColor: !1,
        height: "200px",
        width: "200px",
        lineColor: ['#c9302c'],
        spotColor: ['#088079'],
        minSpotColor: ['#088079'],
        maxSpotColor: ['#088079'],
        normalRangeColor: ['#e9e9e9'],
        normalRangeMin: -1,
        normalRangeMax: 8
    });

    /*---- composite bar chart ----*/
    $(".sparkline-compositebar").sparkline("html", {
        type: "bar",
        height: "200px",
        barWidth: 10,
        barSpacing: 5,
        barColor: ['#088079']
    });

    $(".sparkline-compositebar").sparkline([4, 2, 4, 8, 5, 5, 6, 8, 9, 9, 4, 3, 7, 2, 5, 4, 4, 6, 7, 9], {
        composite: !0,
        fillColor: !1,
        lineColor: ['#c9302c'],
        spotColor: ['#31b0d5']
    });

    /*---- Discrete chart ----*/
    $(".sparkline-discrete").sparkline("html", {
        type: "discrete",
        height: "200px",
        lineColor: ['#ec971f'],
        xwidth: 36
    });

    $(".sparkline-discrete-threshold").sparkline("html", {
        type: "discrete",
        height: "200px",
        lineColor: ['#449d44'],
        thresholdColor: ['red'],
        thresholdValue: 4
    });

    /*---- Bullet chart ----*/
    $(".sparkline-bullet").sparkline("html", {
        type: "bullet",
        height: "60px",
        width: "200px",
        targetColor: ['red'],
        targetWidth: "2",
        performanceColor: ['#da726f'],
        rangeColors: ['#abdaf1', '#8fceec', '#65c5f3']
    });

    /*---- line custom chart ----*/
    $(".sparkline-linecustom").sparkline("html", {
        height: "200px",
        width: "200px",
        lineColor: ['red'],
        fillColor: ['#e9e9e9'],
        minSpotColor: !1,
        maxSpotColor: !1,
        spotColor: ['green'],
        spotRadius: 2
    });

    /*---- tristate chart ----*/
    $(".sparkline-tristate").sparkline("html", {
        type: "tristate",
        height: "150px",
        barWidth: 10,
        barSpacing: 5,
        posBarColor: ['#449d44'],
        negBarColor: ['#bdbdbd'],
        zeroBarColor: ['#c9302c'],
    });
    $(".sparkline-tristatecols").sparkline("html", {
        type: "tristate",
        height: "150px",
        barWidth: 10,
        barSpacing: 5,
        posBarColor: ['#31b0d5'],
        negBarColor: ['#bdbdbd'],
        zeroBarColor: ['#c9302c'],
        colorMap: {
            "-4": ['#c9302c'],
            "-2": ['#31b0d5'],
            2: ['#bdbdbd']
        }
    });

    /*---- boxplot chart ----*/
    $(".sparkline-boxplot").sparkline("html", {
        type: "box",
        height: "150px",
        width: "200px",
        lineColor: ["#ec971f"],
        boxLineColor: ["#ec971f"],
        boxFillColor: ["#e6b36c"],
        whiskerColor: ["grey"],
        medianColor: ["red"]
    });

    $(".sparkline-boxplotraw").sparkline([1, 3, 5, 8, 10, 15, 18], {
        type: "box",
        height: "150px",
        width: "200px",
        raw: !0,
        showOutliers: !0,
        target: 6,
        lineColor: ["#449d44"],
        boxLineColor: ["#449d44"],
        boxFillColor: ["#da726f"],
        whiskerColor: ["grey"],
        outlierLineColor: ["grey"],
        outlierFillColor: ["grey"],
        medianColor: ["#449d44"],
        targetColor: ["green"]
    });

    /*---- Pie chart ----*/
    $(".sparkline-pie-gray").sparkline("html", {
        type: "pie",
        height: "150px",
        sliceColors: ["#ec971f", "grey"]
    });

    $(".sparkline-pie").sparkline("html", {
        type: "pie",
        height: "150px",
        sliceColors: ['#36a9e1', '#4fbcf1', '#71ccf9']
    });

    $(".sparkline-pie-color").sparkline("html", {
        type: "pie",
        height: "150px"
    });
}(document, window, jQuery);