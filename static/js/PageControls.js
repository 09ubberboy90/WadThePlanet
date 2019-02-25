(function ($) {
    var SCROLLING_NAVBAR_OFFSET_TOP = 50;
    $(window).on('scroll', function () {
        var $navbar = $('.navbar');

        if ($navbar.length) {
            if ($navbar.offset().top > SCROLLING_NAVBAR_OFFSET_TOP) {
                $('.scrolling-navbar').addClass('top-nav-collapse');
                $('.sidebar-container').css('background-color', 'rgba(0,0,0,.3)');
            } else {
                $('.scrolling-navbar').removeClass('top-nav-collapse');
                $('.sidebar-container').css('background-color ', ' #1C2331;');
            }
        }
    });
})(jQuery);