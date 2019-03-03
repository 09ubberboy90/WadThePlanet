$(function() {
    // Add elements to top bar if sidebar is collapsed (and vice versa)
    $(window).resize(function () {
        if ($(window).width() >= 975) {
            $('.adder').addClass('collapse');
        } else if ($(window).width() < 975) {
            $('.adder').removeClass('collapse');
        }
    });

    // Move sidebar to top bar depending on size
    $('#menu').on('hidden.bs.collapse', function () {
        $('.adder .sidebar-left').remove();
    });
    $('#menu').on('show.bs.collapse', function () {
        $('.adder').prepend($('#sidebar').html());
    });

    // Trigger top bar animation on scrolling down
    var SCROLLING_NAVBAR_OFFSET_TOP = 50;
    $(window).on('scroll', function () {
        var $navbar = $('.navbar');

        if ($navbar.length) {
            if ($navbar.offset().top > SCROLLING_NAVBAR_OFFSET_TOP) {
                $('#navbar').addClass('top-nav-collapse');
                $('#sidebar').addClass('sidebar-collapse');
            } else {
                $('#navbar').removeClass('top-nav-collapse');
                $('#sidebar').removeClass('sidebar-collapse');
            }
        }
    });
});
