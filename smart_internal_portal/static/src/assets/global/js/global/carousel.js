!function (document, window, $) {
    "use strict";
	if($('#owl-auto-width').length){
		$('#owl-auto-width').owlCarousel({
			margin: 10,
			nav: true,
			loop: true,
			autoWidth: true,
			rtl:true,
			items: 4
		});
	}
	if($('#owl-autoplay').length){
		$("#owl-autoplay").owlCarousel({
			loop: true,
			margin: 10,
			autoplay: true,
			autoplayTimeout: 1000,
			rtl:true,
			autoplayHoverPause: true,
			responsive: {
				0: {
					items: 1
				},
				600: {
					items: 3
				},
				960: {
					items: 4
				},
				1200: {
					items: 4
				}
			}
		});
	}	
	if($('#owl-url').length){
		$('#owl-url').owlCarousel({
			loop: false,
			dots: false,
			center: true,
			margin: 10,
			rtl:true,
			URLhashListener: true,
			autoplayHoverPause: true,
			startPosition: 'URLHash',
			responsive: {
				0: {
					items: 1
				},
				600: {
					items: 3
				},
				960: {
					items: 4
				},
				1200: {
					items: 4
				}
			}
		});
	}
	if($('#owl-full').length){
		$("#owl-full").owlCarousel({
			navigation: true,
			slideSpeed: 400,
			rtl:true,
			paginationSpeed: 500,
			items: 1,
		});
	}
	if($('#owl-full2').length){
		$("#owl-full2").owlCarousel({
			navigation: true,
			slideSpeed: 400,
			rtl:true,
			paginationSpeed: 500,
			items: 1,
		});
	}
	if($('#owl-lazy-load').length){
		$('#owl-lazy-load').owlCarousel({
			items: 4,
			lazyLoad: true,
			loop: true,
			rtl:true,
			margin: 10,
			responsive: {
				0: {
					items: 1
				},
				600: {
					items: 3
				},
				960: {
					items: 4
				},
				1200: {
					items: 4
				}
			}
		});
	}
	if($('#owl-padding').length){
		$('#owl-padding').owlCarousel({
			stagePadding: 50,
			loop: true,
			margin: 10,
			rtl:true,
			dots: false,
			responsive: {
				0: {
					items: 1
				},
				600: {
					items: 1
				},
				1000: {
					items: 1
				}
			}
		});
	}
	if($('#owl-mousewheel').length){
		var owl = $('#owl-mousewheel');
		owl.owlCarousel({
			loop: true,
			nav: true,
			rtl:true,
			dots: false,
			margin: 10,
			navText: [
				"<i class='arrow_carrot-left icon-white'></i>",
				"<i class='arrow_carrot-right icon-white'></i>"
			],
			responsive: {
				0: {
					items: 1
				},
				600: {
					items: 3
				},
				960: {
					items: 4
				},
				1200: {
					items: 5
				}
			}
		});
		owl.on('mousewheel', '.owl-stage', function (e) {
			if (e.deltaY > 0) {
				owl.trigger('next.owl');
			} else {
				owl.trigger('prev.owl');
			}
			e.preventDefault();
		});
	}
	if($('#owl-url').length){
		$('#owl-url').owlCarousel({
			margin: 10,
			nav: true,
			rtl:true,
			autoplay: true,
			responsive: {
				0: {
					items: 1
				},
				480: {
					items: 2
				},
				700: {
					items: 4
				},
				1000: {
					items: 3
				},
				1100: {
					items: 5
				}
			}
		});
	}
	if($('.responsive-slick').length){
		$('.responsive-slick').slick({
			dots: true,
			infinite: false,
			speed: 300,
			rtl:true,
			slidesToShow: 4,
			slidesToScroll: 4,
			responsive: [
				{
					breakpoint: 1024,
					settings: {
						slidesToShow: 3,
						slidesToScroll: 3,
						infinite: true,
						dots: true
					}
				},
				{
					breakpoint: 600,
					settings: {
						slidesToShow: 2,
						slidesToScroll: 2
					}
				},
				{
					breakpoint: 480,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					}
				}
			]
		});
	}
	if($('.single-slick').length){
		$('.single-slick').slick({
			slidesToShow: 1,
			rtl:true,
			responsive: [
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1
					}
				},
				{
					breakpoint: 480,
					settings: {
						slidesToShow: 1
					}
				}
			]
		});
	}
	if($('.center-mode').length){
		$('.center-mode').slick({
			centerMode: true,
			centerPadding: '60px',
			slidesToShow: 3,
			rtl:true,
			responsive: [
				{
					breakpoint: 768,
					settings: {
						centerMode: true,
						centerPadding: '40px',
						slidesToShow: 3
					}
				},
				{
					breakpoint: 480,
					settings: {
						centerMode: true,
						centerPadding: '40px',
						slidesToShow: 1
					}
				}
			]
		});
	}
	if($('.slider-nav').length){
		$('.slider-nav').slick({
			slidesToShow: 5,
			slidesToScroll: 1,
			asNavFor: '.slider-for',
			dots: true,
			rtl:true,
			centerMode: true,
			focusOnSelect: true,
			slickSetOption: true,
			responsive: [
				{
					breakpoint: 480,
					settings: {
						slidesToShow: 2,
					}
				}
			]
		});
	}
	if($('.slider-for').length){
		$('.slider-for').slick({
			slidesToShow: 1,
			slidesToScroll: 1,
			arrows: false,
			fade: true,
			rtl:true,
			slickSetOption: true,
			asNavFor: '.slider-nav',
			responsive: [
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1
					}
				},
				{
					breakpoint: 480,
					settings: {
						slidesToShow: 1
					}
				},
				{
					breakpoint: 320,
					settings: {
						slidesToShow: 1
					}
				}
			]
		});
	}
	if($('.fade-slide').length){
		$('.fade-slide').slick({
			dots: true,
			infinite: true,
			slickSetOption: true,
			speed: 500,
			rtl:true,
			fade: true,
			cssEase: 'linear',
			responsive: [
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1
					}
				},
				{
					breakpoint: 480,
					settings: {
						slidesToShow: 1
					}
				},
				{
					breakpoint: 320,
					settings: {
						slidesToShow: 1
					}
				}
			]
		});
	}
	if($('.multiple-items').length){
		$('.multiple-items').slick({
			infinite: true,
			slidesToShow: 3,
			rtl:true,
			slidesToScroll: 3,
			responsive: [
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 3
					}
				},
				{
					breakpoint: 480,
					settings: {
						slidesToShow: 3
					}
				},
				{
					breakpoint: 320,
					settings: {
						slidesToShow: 2
					}
				}
			]
		});
	}

}(document, window, jQuery);

$(window).resize(function () {
	if($('.slider-for').length){$('.slider-for').slick('refresh');}
	if($('.fade-slide').length){$('.fade-slide').slick('refresh');}
});
