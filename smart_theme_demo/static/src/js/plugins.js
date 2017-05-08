// Avoid `console` errors in browsers that lack a console.
(function() {
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());

var windowWi = window.innerWidth;
var windowHe = window.innerHeight;
//screen width
//$('body').append('<div style="position:fixed;top:150px;left:20px;padding:10px;font-size:20px;color: green;background:#fff;">'+windowWi+'</div>');

/*#################################################################################################################*/
/*#################################################################################################################*/
(function($) {

	$(document).ready(function() {

		jQuery('body').append('<div id="canvas-wrapper">' +
								'<canvas id="demo-canvas"></canvas>' +
							  '</div>');
		// Init CanvasBG
		CanvasBG.init({
			Loc: {
				x: window.innerWidth / 10,
				y: window.innerHeight / 20
			}
		});
	});

})(jQuery);
/*#################################################################################################################*/
/*#################################################################################################################*/

/***********************************************************************************************************************************************
 *********************************************					equalHeight						************************************************
 ***********************************************************************************************************************************************/
function equalHeight(group) {
    if ($(window).width() > 767) {
        var tallest = 0;
        group.each(function () {
            var thisHeight = $(this).height();
            if (thisHeight > tallest) {
                tallest = thisHeight;
            }
        });
    } else {
        tallest = 'auto';
    }
    group.height(tallest);
}

/***********************************************************************************************************************************************
 ***********************************************************************************************************************************************
 ***********************************************************************************************************************************************
 ***********************************************************************************************************************************************/
(function (window, $) {

    $(function () {
        $('.ripple').on('click', function (event) {
            event.preventDefault();

            var $div = $('<div/>'),
                btnOffset = $(this).offset(),
                  xPos = event.pageX - btnOffset.left,
                  yPos = event.pageY - btnOffset.top;

            $div.addClass('ripple-effect');
            var $ripple = $(".ripple-effect");

            $ripple.css("height", $(this).height());
            $ripple.css("width", $(this).height());
            $div
              .css({
                  top: yPos - ($ripple.height() / 2),
                  left: xPos - ($ripple.width() / 2),
                  background: $(this).data("ripple-color")
              })
              .appendTo($(this));

            window.setTimeout(function () {
                $div.remove();
            }, 2000);
        });

    });
})(window, jQuery);

/***********************************************************************************************************************************************
 *********************************************					tableToExcel						************************************************
 ***********************************************************************************************************************************************
 ***********************************************************************************************************************************************/
var tableToExcel = (function() {
  var uri = 'data:application/vnd.ms-excel;base64,'
	, template = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>{worksheet}</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--><meta http-equiv="content-type" content="text/plain; charset=UTF-8"/></head><body><table>{table}</table></body></html>'
	, base64 = function(s) { return window.btoa(unescape(encodeURIComponent(s))) }
	, format = function(s, c) { return s.replace(/{(\w+)}/g, function(m, p) { return c[p]; }) }
  return function(table, name) {
	if (!table.nodeType) table = document.getElementById(table)
	var ctx = {worksheet: name || 'Worksheet', table: table.innerHTML}
	window.location.href = uri + base64(format(template, ctx))
  }
})();

/***********************************************************************************************************************************************
 ***********************************************************************************************************************************************
 ***********************************************************************************************************************************************
 ***********************************************************************************************************************************************/