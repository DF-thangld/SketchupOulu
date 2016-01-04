/*!
 * Start Bootstrap - Creative Bootstrap Theme (http://startbootstrap.com)
 * Code licensed under the Apache License v2.0.
 * For details, see http://www.apache.org/licenses/LICENSE-2.0.
 */

$( document ).ready(function() {
	// jQuery for page scrolling feature - requires jQuery Easing plugin
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: ($($anchor.attr('href')).offset().top - 50)
        }, 1250, 'easeInOutExpo');
        event.preventDefault();
    });

    // Highlight the top nav as scrolling occurs
    $('body').scrollspy({
        target: '.navbar-fixed-top',
        offset: 51
    })

    // Closes the Responsive Menu on Menu Item Click
    $('.navbar-collapse ul li a').click(function() {
        $('.navbar-toggle:visible').click();
    });

    // Fit Text Plugin for Main Header
    $("h1").fitText(
        1.2, {
            minFontSize: '35px',
            maxFontSize: '65px'
        }
    );

    // Offset for Main Navigation
    $('#mainNav').affix({
        offset: {
            top: 100
        }
    })

    // Initialize WOW.js Scrolling Animations
    new WOW().init();

});

jQuery.fn.extend({
  autoHeight: function () {
    function autoHeight_(element) {
      return jQuery(element)
        .css({ 'height': 'auto', 'overflow-y': 'hidden' })
        .height(element.scrollHeight);
    }
    return this.each(function() {
      autoHeight_(this).on('input', function() {
        autoHeight_(this);
      });
    });
  }
});

function show_alert(alert_type, alert_content)
{
    $('#alert_panel').addClass(alert_type);
    $('#alert_content').html(alert_content);
    $('#alert_panel').fadeIn();
    setTimeout(function(){
        $('#alert_panel').fadeOut(function(){$('#alert_panel').removeClass(alert_type);});

    }, 3000);
}

function format_date(date)
{
    var result = '';
    result += date.getDate().toString() + '.' + date.getMonth().toString() + '.' + date.getFullYear().toString() + ' ';
    result += date.getHours().toString() + ':' + date.getMinutes().toString() + ':' + date.getSeconds().toString();
    return result;
}

