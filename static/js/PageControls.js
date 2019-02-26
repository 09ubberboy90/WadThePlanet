(function ($) {
    var SCROLLING_NAVBAR_OFFSET_TOP = 50;
    $(window).on('scroll', function () {
        var $navbar = $('.navbar');

        if ($navbar.length) {
            if ($navbar.offset().top > SCROLLING_NAVBAR_OFFSET_TOP) {
                $('.scrolling-navbar').addClass('top-nav-collapse');
                $('.sidebar-container').css('background-color', '#1C2331');
            } else {
                $('.scrolling-navbar').removeClass('top-nav-collapse');
                $('.sidebar-container').css('background-color', 'rgba(0,0,0,.3)');
            }
        }
    });
})(jQuery);
$(function() {
    $('#menu').on('hidden.bs.collapse', function () {
        $('.adder .sidebar-left').remove();
    })
    $('#menu').on('show.bs.collapse', function () {
        $('.adder').prepend($('#sidebar').html());
    })
    $(window).resize(function () {
        if ($(window).width() >= 975){
            $('.adder').addClass('collapse');
        }
        else if ($(window).width() < 975) {
            $('.adder').removeClass('collapse');
        }
    });
});
$(document).ready(function() {
    var navheight = $('#navbar').outerHeight();
    $('.main-screen').css('padding-top', navheight);
});
