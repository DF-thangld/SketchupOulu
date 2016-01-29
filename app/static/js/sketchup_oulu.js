/*!
 * Start Bootstrap - Creative Bootstrap Theme (http://startbootstrap.com)
 * Code licensed under the Apache License v2.0.
 * For details, see http://www.apache.org/licenses/LICENSE-2.0.
 */

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
 
 
$( document ).ready(function() {
	// jQuery for page scrolling feature - requires jQuery Easing plugin
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: ($($anchor.attr('href')).offset().top - 50)
        }, 1250, 'easeInOutExpo');
        event.preventDefault();
    });
	
	$('textarea').autoHeight();

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

function add_comment()
{
    if ($('#new_comment').val().trim() == '')
    {
        show_alert('alert-danger', 'Comment content is required');
        return;
    }
    $.ajax({
        type: "POST",
        url: add_comment_url,
        data: {'comment_type': $('#comment_type').val(),
                'object_id': $('#object_id').val(),
                'content': $('#new_comment').val()},
        dataType: 'json',
        success: function(data)
        {
            var new_comment_html = '';
            new_comment_html += '<li><div class="commenterImage"><img style="max-width:50px;max-height:50px;" src="' + profile_url + '/' + data.owner.profile_picture + '" /></div>';
            new_comment_html += '<div class="commentText"><p class="">' + data.content + '</p> <span class="date sub-text">By ' + data.owner.username + ' on ' + Date.parse(data.created_time).toString('dd.MM.yyyy hh:mm:ss') + '</span></div></li>';
            $('#comment_list').prepend(new_comment_html);
            show_alert('alert-success', 'Comment added');
            $('#new_comment').val('');
        },
        error: function(data)
        {
            show_alert('alert-danger', data.responseJSON[0]);
        }
    });
}

function display_edit_comment_form()
{
    show_alert('alert-danger', 'Function not yet implemented :)');
}

function delete_comment(comment_id)
{
    $.ajax({
        type: "POST",
        url: delete_comment_url,
        data: {'comment_id': comment_id},
        dataType: 'json',
        success: function(data)
        {
            $('#comment_' + data.comment_id).remove();
            //show_alert('alert-success', 'Comment deleted');
        },
        error: function(data)
        {
            show_alert('alert-danger', data.responseJSON[0]);
        }
    });
}
function edit_comment(comment_id)
{
    show_alert('alert-danger', 'Function not yet implemented :)');
}
