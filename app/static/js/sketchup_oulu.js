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

function redraw_scenario_ground(current_scene)
{
    // remove old line
    current_scene.remove( current_scene.getObjectByName('ground_layout') );
    current_scene.remove( current_scene.getObjectByName('ground') );

    // redraw plane ground
    if (current_scene.hasOwnProperty('world_size'))
        WORLD_SIZE = current_scene.world_size;
    var size = WORLD_SIZE/2, step = BLOCK_SIZE;

	var geometry = new THREE.Geometry();

	for ( var i = - size; i <= size; i += step ) {

		geometry.vertices.push( new THREE.Vector3( - size, 0, i ) );
		geometry.vertices.push( new THREE.Vector3(   size, 0, i ) );

		geometry.vertices.push( new THREE.Vector3( i, 0, - size ) );
		geometry.vertices.push( new THREE.Vector3( i, 0,   size ) );

	}

	var material = new THREE.LineBasicMaterial( { color: 0x000000, opacity: 0.5, transparent: true } );

	var line = new THREE.LineSegments( geometry, material );
    line.name = 'ground_layout';
	current_scene.add( line );

	//create the lowest base, unvisible, just used for detect where to place the models
	geometry = new THREE.PlaneBufferGeometry( WORLD_SIZE, WORLD_SIZE );
	geometry.rotateX( - Math.PI / 2 );

	plane = new THREE.Mesh( geometry, new THREE.MeshBasicMaterial( { visible: false } ) );
    plane.name = 'layout';
	current_scene.add( plane );
}

function init_scene(information, current_scene)
{
    WORLD_SIZE = 1000;
    for (var model_id in information)
	{
        if (model_id.substring(0, 6) == 'model_')
        {
            var model = information[model_id];
            load_model( model.file_type,
                        model_path + model.directory + '/',
                        model.original_filename,
                        model,
                        current_scene);
        }
        else if (model_id == 'size')
        {
            WORLD_SIZE = information['size'];
        }
	}
    current_scene.world_size = WORLD_SIZE;
    redraw_scenario_ground(current_scene);
}

function enlarge_scenario()
{
    // define new value
    WORLD_SIZE += 100;
    scene.world_size = WORLD_SIZE;
    redraw_scenario_ground(scene);
}

function shrink_scenario()
{
    // define new value
    WORLD_SIZE -= 100;
    scene.world_size = WORLD_SIZE;
    redraw_scenario_ground(scene);
}

function find_by_id(array, id)
{
    var length = array.length;
    for (i=0; i<length; i++)
    {
        if (array[i].id == id)
            return array[i];
    }
    return null;
}

function generate_random_string(length)
{

    var possible_1 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    var possible_2 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

    var text = possible_1.charAt(Math.floor(Math.random() * possible_1.length));
    for( var i=1; i < length; i++ )
        text += possible_2.charAt(Math.floor(Math.random() * possible_2.length));

    return text;
}

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

var loaded_objects = {};
var manager = new THREE.LoadingManager();
function load_model(file_type, directory, filename, addition_information, object_scene, onload)
{
    if (directory.substr(directory.length - 2) == "//")
        directory = directory.substr(0, directory.length - 1);
    if (directory.substr(directory.length - 1) != "/")
        directory = directory + '/';
    var unique_id = file_type + "|" + directory + "|" + filename;

    if (!addition_information.hasOwnProperty('size'))
        addition_information.size = 1;
    if (!addition_information.hasOwnProperty('x'))
        addition_information.x = 0;
    if (!addition_information.hasOwnProperty('y'))
        addition_information.y = 0;
    if (!addition_information.hasOwnProperty('z'))
        addition_information.z = 0;
    if (!addition_information.hasOwnProperty('rotate_x'))
        addition_information.rotate_x = 0;
    if (!addition_information.hasOwnProperty('rotate_y'))
        addition_information.rotate_y = 0;
    if (!addition_information.hasOwnProperty('rotate_z'))
        addition_information.rotate_z = 0;

    if (unique_id in loaded_objects)
    {
        if (loaded_objects[unique_id] == null)
        {
            setTimeout(function(){
                load_model(file_type, directory, filename, addition_information, object_scene, onload)
            }, 50);
            return;
        }
        var new_object = loaded_objects[unique_id].clone();

        new_object.scale.x = new_object.scale.y = new_object.scale.z = addition_information.size;
        new_object.position.x = addition_information.x;
        new_object.position.y = addition_information.y;
        new_object.position.z = addition_information.z;

        new_object.rotation.x = addition_information.rotate_x;
        new_object.rotation.y = addition_information.rotate_y;
        new_object.rotation.z = addition_information.rotate_z;

        new_object.name = addition_information.id;
        object_scene.add( new_object );
        if ( onload !== undefined )
            onload(new_object);
        return;
    }
    loaded_objects[file_type + "|" + directory + "|" + filename] = null;
    if (file_type == 'objmtl')
    {
        var loader = new THREE.OBJMTLLoader(manager);
        loader.load(directory + filename + ".obj",
            directory + filename + ".mtl",
            function ( object )
        {
            object.scale.x = object.scale.y = object.scale.z = addition_information.size;
            object.position.x = addition_information.x;
            object.position.y = addition_information.y;
            object.position.z = addition_information.z;
            object.rotation.x = addition_information.rotate_x;
            object.rotation.y = addition_information.rotate_y;
            object.rotation.z = addition_information.rotate_z;
            object.name = addition_information.id;

            loaded_objects[file_type + "|" + directory + "|" + filename] = object;

            object_scene.add( object );
            if ( onload !== undefined )
                onload(object);
        });
    }
    else if (file_type == 'obj')
    {
        var loader = new THREE.OBJLoader(manager);
        var file_url = directory + filename;
        if (file_url.substr(file_url.length - 4) != ".obj")
            file_url = file_url + ".obj";

        loader.load(file_url,
        function ( object )
        {
            //object = object.children[0];
            object.scale.x = object.scale.y = object.scale.z = addition_information.size;
            object.position.x = addition_information.x;
            object.position.y = addition_information.y;
            object.position.z = addition_information.z;
            object.rotation.x = addition_information.rotate_x;
            object.rotation.y = addition_information.rotate_y;
            object.rotation.z = addition_information.rotate_z;
            object.name = addition_information.id;

            loaded_objects[file_type + "|" + directory + "|" + filename] = object;

            object_scene.add( object );
            if ( onload !== undefined )
                onload(object);
        });
    }
    else if (file_type == 'dae')
    {
        var loader = new THREE.ColladaLoader(manager);
        loader.options.upAxis = 'X'; // Rotation by 90 degrees
        loader.options.convertUpAxis = true; // Align the Y-axis
        loader.load(directory + filename + ".dae", function (collada)
        {
            dae = collada.scene;
            dae.scale.x = dae.scale.y = dae.scale.z = addition_information.size;
            dae.position.x = addition_information.x;
            dae.position.y = addition_information.y;
            dae.position.z = addition_information.z;
            dae.rotation.x = addition_information.rotate_x;
            dae.rotation.y = addition_information.rotate_y;
            dae.rotation.z = addition_information.rotate_z;
            dae.name = addition_information.id;
            loaded_objects[file_type + "|" + directory + "|" + filename] = dae;
            object_scene.add(dae);
            if ( onload !== undefined )
                onload(dae);
        });
    }

}