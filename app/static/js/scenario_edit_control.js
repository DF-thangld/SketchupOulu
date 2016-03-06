var TRIM_SCREEN_VALUE = 7;
var SCREEN_WIDTH = window.screen.availWidth;
var SCREEN_HEIGHT = window.screen.availHeight;
var WORLD_SIZE = 1000; //side length of the square world
var BLOCK_SIZE = 50;
var MOVING_SPEED = 10;
var DEFAULT_HEIGHT = 1000;
var DEFAULT_DISTANCE = 100;
var views = [{'x': 0, 'y':DEFAULT_HEIGHT, 'z': -1*WORLD_SIZE-DEFAULT_DISTANCE},
 			{'x': WORLD_SIZE+DEFAULT_DISTANCE, 'y':DEFAULT_HEIGHT, 'z': 0},
 			{'x': 0, 'y':DEFAULT_HEIGHT, 'z': WORLD_SIZE+DEFAULT_DISTANCE},
 			{'x': -1*WORLD_SIZE-DEFAULT_DISTANCE, 'y':DEFAULT_HEIGHT, 'z': 0}];
var center_position = new THREE.Vector3( 0, 0, 0 );

// required variables
var fullscreen_element = 'fullscreen_area';
var scenario_element = 'ModelWindow';
var control_element = 'ControlWindow';
var controlling_scene = null;
var controlling_renderer = null;
var controlling_camera = null;
var control = null;


// variables
var mode_index = -1;
var actions = [];
var redo_actions = [];
var building_scenes = [];
var temp_variable = null;
var is_fullscreen = false;
var old_width = 0;
var old_height = 0;
var current_width = 0;
var current_height = 0;
var old_control_window_height = 500;
var mouse_on_model = false;
var building_renderer = null;
var IsOnTop=false;

var isShiftDown = false;
var isControlDown = false;




$( document ).ready(function()
{
	$('#ModelWindow').hover(function(){mouse_on_model = true;},function(){mouse_on_model = false;});
	document.addEventListener( 'keydown', onDocumentKeyDown, false );
	document.addEventListener( 'keyup', onDocumentKeyUp, false );
	window.addEventListener( 'resize', onWindowResize, false );
	// add mouse events to mode
	document.addEventListener( 'mousemove', onDocumentMouseMove, false );
	document.addEventListener( 'mousedown', onDocumentMouseDown, false );
	document.addEventListener( 'mouseup', onDocumentMouseUp, false );
	change_build_place();
});

function animate() 
{
	requestAnimationFrame( animate );
	if (isShiftDown && (mouse_on_model || is_fullscreen))
	{
		control.enabled = true;
		control.update();
		var metric= Math.ceil( controlling_camera.position.y/10 );
    	document.getElementById("metric").innerHTML=metric +"m";
	}
	else
		control.enabled = false;
	//console.log(isShiftDown, mouse_on_model, is_fullscreen);
	render();
}

function render() 
{
	for (i=0; i < building_models.length; i++)
    {
        var building_model = building_models[i];
        building_model['renderer'].render( building_model['scene'], building_model['camera'] );
    }
	controlling_renderer.render( controlling_scene, controlling_camera );
}

function init()
{
	windowRatio = document.getElementById("ModelWindow").offsetWidth/document.getElementById("ModelWindow").offsetHeight;
	windowWidth = document.getElementById("ModelWindow").offsetWidth;
	windowHeight = document.getElementById("ModelWindow").offsetHeight;

	scene = new THREE.Scene();
    scene.name = "add_scenario_scene";
	
	isSelect = false;// no object has been selected
	selectedModel = null;
	
	//load model information
	THREE.Loader.Handlers.add( /\.dds$/i, new THREE.DDSLoader() );

	//pre-defined objects
    init_scene(sceneObjects, scene, function(model){
		objects.push(model);
	});

	//document
	//container = document.createElement( 'div' );
	//document.body.appendChild( container );
	
	container = document.getElementById("ModelWindow");
	//webgl
	camera = new THREE.PerspectiveCamera( 45, windowRatio, 1, 10000 );
	camera.position.set( views[0].x, views[0].y, views[0].z );
	camera.target = center_position;
	camera.lookAt( camera.target );

	//light
	var ambient = new THREE.AmbientLight( 0xffffff );
	scene.add( ambient );

	// display the scene
	if (window.WebGLRenderingContext)
		renderer = new THREE.WebGLRenderer( { antialias: true } );//using WebGL
	else
		renderer = new THREE.CanvasRenderer(); //using the (slower) Canvas 2D Context API

	renderer.setClearColor( 0xf0f0f0 ); //0xffffff
	renderer.setPixelRatio( window.devicePixelRatio );
	//renderer.setPixelRatio( document.getElementById("ModelWindow").offsetWidth/
	//						document.getElementById("ModelWindow").offsetHeight );
	renderer.setSize( 	document.getElementById("ModelWindow").offsetWidth,
		 				document.getElementById("ModelWindow").offsetHeight
	);
	
	container.appendChild( renderer.domElement );
	controls = new THREE.OrbitControls( camera, renderer.domElement );

	//intersectObjects=[plane];
	objects.push(plane);
	intersectObjects = objects;
	//render
	renderer.render( scene, camera);
	control = controls;
	controlling_renderer = renderer;
	controlling_scene = scene;
	controlling_camera = camera;
}

function init_building_model(id, file_type, information, index, has_preview)
{
	$('#building_model_' + id).css('height', $('#building_model_' + id).width()*3/4);
	if (has_preview != 1)
	{
	    information = JSON.parse(information);
	
	    // variables
	    var building_scene = new THREE.Scene();
	    building_scene.name = "scene_building_model_" + id;
	    var SCREEN_WIDTH = $('#building_model_' + id).innerWidth()-8, SCREEN_HEIGHT = $('#building_model_' + id).innerHeight()-8;
	    var VIEW_ANGLE = 45, ASPECT = SCREEN_WIDTH / SCREEN_HEIGHT, NEAR = 1, FAR = 10000;
	    var building_camera = new THREE.PerspectiveCamera( VIEW_ANGLE, ASPECT, NEAR, FAR);
	    building_camera.position.set(information.camera_x, information.camera_y, information.camera_z*1.5);
	    building_camera.lookAt(new THREE.Vector3( information.camera_lookat_x, information.camera_lookat_y, information.camera_lookat_z ));
	    building_scene.add(building_camera);
	    building_scene.userData.camera = building_camera;
	    building_scene.userData.building_id = id;
	    building_scenes.push(building_scene);
	    
	    // RENDERER
	    if (building_renderer == null)
	    {
		    if ( Detector.webgl )
		        building_renderer = new THREE.WebGLRenderer( {antialias:true} );
		    else
		        building_renderer = new THREE.CanvasRenderer();
		    building_renderer.setSize(1000, 1000*3/4);
	    }
	    //var building_container = document.getElementById( 'building_model_' +id );
	    //building_container.appendChild( building_renderer.domElement );
	
	    //LIGHT
	    var ambientLight = new THREE.AmbientLight(0xffffff);
	    building_scene.add(ambientLight);
	}

    //object
    load_model( file_type,
    			MODEL_PATH + information.directory + '/',
                information.original_filename,
                {'id': id, 'x': 0, 'y': 0, 'z': 0, 'size': 1, 'rotate_x': 0, 'rotate_y': 0, 'rotate_z': 0},
                building_scene,
                function(object)
                {
                    models[index] = object;
                });

    //move objects to global arrays
    //building_models.push({"id": id, "renderer": building_renderer, 'camera': building_camera, 'scene': building_scene});
    //building_renderer.render( building_scene, building_camera );
}

manager.onLoad = function()
{
	if (building_scenes.length > 0)
		building_renderer.setSize( 1000, 1000*3/4 );
	for (i=0; i < building_scenes.length; i++)
    {
		var scene = building_scenes[i];
		var id = scene.userData.building_id;
		building_renderer.setClearColor( 0xffffff );
        building_renderer.setScissorTest( false );
        building_renderer.clear();
        building_renderer.render(scene, scene.userData.camera);
        var image_url = building_renderer.domElement.toDataURL( 'image/png' );
        $('#building_model_' + id).html('<img src="' + image_url + '" style="width:100%; height:100%"/>');
        $.ajax({
            type: "POST",
            url: UPDATE_BUILDING_MODEL_URL + id,
            data: {'preview': image_url},
            dataType: 'json',
            error: function(data)
            {
                show_alert('alert-danger', data.responseJSON[0]);
            }
        });
    }
	renderer.setSize( 	document.getElementById("ModelWindow").offsetWidth,document.getElementById("ModelWindow").offsetHeight);
		
}

function add_building_model(information)
{
    if (current_object != null)
    	controlling_scene.remove(current_object);
    
    model_options = {'id': "model_" + generate_random_string(50), 'x': 0, 'y': 0, 'z': 0, 'size': 1, 'rotate_x': 0, 'rotate_y': 0, 'rotate_z': 0};
    
	load_model( information.file_type,
				MODEL_PATH + information.directory + '/',
				information.original_filename,
				model_options,
				controlling_scene,
				function(object)
				{
					current_object = object;
					object.addition_information = information;
					switchMode(1);
					buttons = {'0': 'btn_move_model', '2': 'btn_delete_model', '3': 'btn_enlarge_model', '4': 'btn_shrink_model', '5': 'btn_rotate_left', '6': 'btn_rotate_right'};
			    	for (var mode_key in buttons)
						$('#' + buttons[mode_key]).removeClass('disabled');
				});
}

function change_build_place()
{
	if(IsOnTop)
	{
		//change to build on ground mode
		IsOnTop=false;
		intersectObjects=[plane];
		//objects.splice( objects.indexOf( plane ), 1 );
		document.getElementById("buildWhere").innerHTML="Build On Ground";
	}
	else
	{
		//change to build on top mode
		IsOnTop=true;
		
		intersectObjects=objects;
		document.getElementById("buildWhere").innerHTML="Build On Top";
	}

}

function switchMode(i)
{
	var mode = parseInt(i);
	if(mode_index ==1 && mode!=1){// from 0 to other
		current_object.visible=false;
	}else if(mode_index !=1 && mode==1){
		current_object.visible=true;
	}
	mode_index = mode;
	switch(mode){
		case 0:{
			break;
		}
		case 1:{
			break;
		}
		case 7:{
			var preview = document.getElementById( "preview" );
			var file    = document.querySelector('input[type=file]').files[0]; //sames as here
			var reader  = new FileReader();
			reader.onloadend = function () {
				preview.src = reader.result;
				
				var loader = new THREE.TextureLoader();
				loader.load(reader.result,function(texture){
					var geometry = new THREE.SphereGeometry( 200, 25, 200 );
					var material = new THREE.MeshBasicMaterial( { map: texture, overdraw: true } );
					var mesh = new THREE.Mesh( geometry, material );
					plane.material= material;
				} );
			}

			if (file) {
				reader.readAsDataURL(file); //reads the data as a URL
			} else {
				preview.src = "";
			}
			break;
		}
		
	}
}

function undo_action(on_finish)
{
	action = actions.pop();
	if (action == null)
		return;
	redo_actions.push(action);
	
	//user interface change
	if (actions.length == 0)
		$('#btn_undo_action').addClass('disabled');
	$('#btn_redo_action').removeClass('disabled');
	
	switch(action['action'])
	{
		case 'MOVE':
			var object = controlling_scene.getObjectByName(action['object_id']);
			
			object.position.x = action['old_value']['x'];
			object.position.y = action['old_value']['y'];
			object.position.z = action['old_value']['z'];
			
			//update modelInfos as well
			var selected_model = sceneObjects[action['object_id']];
			selected_model.x = action['old_value']['x'];
			selected_model.y = action['old_value']['y'];
			selected_model.z = action['old_value']['z'];
			break;
		case 'ADD_MODEL':
			var object = controlling_scene.getObjectByName(action['object_id']);
			controlling_scene.remove(object);
			delete sceneObjects[action['object_id']];
			objects.splice( objects.indexOf( object ), 1 );
			break;
		case 'DELETE_MODEL':
			controlling_scene.add(action['old_value']['scene_object']);
			sceneObjects[action['object_id']] = action['old_value']['object'];
			objects.push(action['old_value']['scene_object']);
			break;
		case 'RESIZE_MODEL':
			var object = controlling_scene.getObjectByName(action['object_id']);
			object.scale.x = action['old_value'];
			object.scale.y = action['old_value'];
			object.scale.z = action['old_value'];
			sceneObjects[action['object_id']].size = action['old_value'];
			break;
		case 'ROTATE_MODEL':
			var object = controlling_scene.getObjectByName(action['object_id']);
			object.rotation.x = action['old_value'].x;
			object.rotation.y = action['old_value'].y;
			object.rotation.z = action['old_value'].z;
			
			sceneObjects[action['object_id']].rotate_x = action['old_value'].x;
			sceneObjects[action['object_id']].rotate_y = action['old_value'].y;
			sceneObjects[action['object_id']].rotate_z = action['old_value'].z;
			break;
		case 'RESIZE_SCENE':
			WORLD_SIZE = action['old_value'];
		    controlling_scene.world_size = WORLD_SIZE;
		    redraw_scenario_ground(controlling_scene);
		    break;
	}
	
	if (on_finish !== undefined)
		on_finish(action);
}

function redo_action(on_finish)
{
	action = redo_actions.pop();
	if (action == null)
		return;
	actions.push(action);
	
	//user interface change
	if (redo_actions.length == 0)
		$('#btn_redo_action').addClass('disabled');
	$('#btn_undo_action').removeClass('disabled');
	
	switch(action['action'])
	{
		case 'MOVE':
			var object = controlling_scene.getObjectByName(action['object_id']);
			
			object.position.x = action['new_value']['x'];
			object.position.y = action['new_value']['y'];
			object.position.z = action['new_value']['z'];
			
			//update modelInfos as well
			var selected_model = sceneObjects[action['object_id']];
			selected_model.x = action['new_value']['x'];
			selected_model.y = action['new_value']['y'];
			selected_model.z = action['new_value']['z'];
			break;
		case 'ADD_MODEL':
			controlling_scene.add(action['new_value']['scene_object']);
			sceneObjects[action['object_id']] = action['new_value']['object'];
			objects.push(action['new_value']['scene_object']);
			break;
		case 'DELETE_MODEL':
			var object = controlling_scene.getObjectByName(action['object_id']);
			controlling_scene.remove(object);
			delete sceneObjects[action['object_id']];
			objects.splice( objects.indexOf( object ), 1 );
			break;
		case 'RESIZE_MODEL':
			var object = controlling_scene.getObjectByName(action['object_id']);
			object.scale.x = action['new_value'];
			object.scale.y = action['new_value'];
			object.scale.z = action['new_value'];
			sceneObjects[action['object_id']].size = action['new_value'];
			break;
		case 'ROTATE_MODEL':
			var object = controlling_scene.getObjectByName(action['object_id']);
			object.rotation.x = action['new_value'].x;
			object.rotation.y = action['new_value'].y;
			object.rotation.z = action['new_value'].z;
			
			sceneObjects[action['object_id']].rotate_x = action['new_value'].x;
			sceneObjects[action['object_id']].rotate_y = action['new_value'].y;
			sceneObjects[action['object_id']].rotate_z = action['new_value'].z;
			break;
		case 'RESIZE_SCENE':
			WORLD_SIZE = action['new_value'];
		    controlling_scene.world_size = WORLD_SIZE;
		    redraw_scenario_ground(controlling_scene);
		    break;
	}
	
	if (on_finish !== undefined)
		on_finish(action);
}




function onDocumentKeyDown(event)
{
	if (mouse_on_model || is_fullscreen)
	{
		event.preventDefault();
	}
	switch ( event.keyCode ) 
	{
		case 16: isShiftDown = true; break; //shift, delete mode with click
		case 17: isControlDown = true; break;
		case 38: move_forward = true; break; // up
		case 40: move_backward = true; break; // down
		case 37: move_left = true; break; // left
		case 39: move_right = true; break; // right
		case 87: move_up = true; break; // w
		
		case 188: // <
			if ((mouse_on_model || is_fullscreen) && isControlDown && isShiftDown)
			{
				if (mode_index == 0 && selectedModel != null)
				{
					var old_scale = controlling_scene.getObjectByName(selectedModel.name).scale.x;
				
					controlling_scene.getObjectByName(selectedModel.name).scale.multiplyScalar( 1.05 );
					sceneObjects[selectedModel.name].size = controlling_scene.getObjectByName(selectedModel.name).scale.x;
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'RESIZE_MODEL', 
						'object_id': selectedModel.name, 
						'old_value': old_scale, 
						'new_value': controlling_scene.getObjectByName(selectedModel.name).scale.x});
				}
			}
			break;
		case 190: // >
			if ((mouse_on_model || is_fullscreen) && isControlDown && isShiftDown)
			{
				if (mode_index == 0 && selectedModel != null)
				{
					var old_scale = controlling_scene.getObjectByName(selectedModel.name).scale.x;
				
					controlling_scene.getObjectByName(selectedModel.name).scale.divideScalar( 1.05 );
					sceneObjects[selectedModel.name].size = controlling_scene.getObjectByName(selectedModel.name).scale.x;
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'RESIZE_MODEL', 
						'object_id': selectedModel.name, 
						'old_value': old_scale, 
						'new_value': controlling_scene.getObjectByName(selectedModel.name).scale.x});
				}
			}
			break;
		
		case 189: // -
			if ((mouse_on_model || is_fullscreen) && isControlDown && isShiftDown)
				shrink_scenario();
			break;
		case 187: // +
			if ((mouse_on_model || is_fullscreen) && isControlDown && isShiftDown)
				enlarge_scenario();
			break;
		case 83: // s
			move_down = true; 
			if ((mouse_on_model || is_fullscreen) && isControlDown)
				save_scenario_content();
			break; 
		case 89: // z
			if ((mouse_on_model || is_fullscreen) && isControlDown)
			{
				redo_action();
			}
			break; 
		case 90: // y
			if ((mouse_on_model || is_fullscreen) && isControlDown)
			{
				undo_action();
			}
			break; 
		case 70 : // f
			if ((mouse_on_model || is_fullscreen) && isControlDown)
			{
				full_screen();
			}
			break;
	}
}

function onDocumentKeyUp(event)
{
	if (mouse_on_model || is_fullscreen)
		event.preventDefault();
	switch ( event.keyCode ) 
	{
		case 16: isShiftDown = false; break; //shift
		case 17: isControlDown = false; break;
		case 38: move_forward = false; break; // up
		case 40: move_backward = false; break; // down
		case 37: move_left = false; break; // left
		case 39: move_right = false; break; // right
		case 87: move_up = false; break; // w
		case 83: move_down = false; break; // s
		case 90: is_rotating = false; break; // z

	}
}

function onDocumentMouseMove(event)
{
	var x = event.pageX - $('#ModelWindow').offset().left;
	var y = event.pageY - $('#ModelWindow').offset().top;
	var div_width =document.getElementById("ModelWindow").clientWidth;
	var div_height=document.getElementById("ModelWindow").clientHeight;
	
	
	switch(mode_index)
	{
		case 0:{//select mode
			if(isSelect == true){
				mouse.set( ( x / div_width ) * 2 - 1, - ( y / div_height ) * 2 + 1 );

				raycaster.setFromCamera( mouse, camera );

				var intersects = raycaster.intersectObjects( [plane], true );
				if ( intersects.length > 0 )
				{

					selectedModel.position.x = intersects[0].point.x;
					selectedModel.position.y = intersects[0].point.y;
					selectedModel.position.z = intersects[0].point.z;
					
					//update modelInfos as well
					var selected_model = sceneObjects[selectedModel.name];
					selected_model.x = selectedModel.position.x;
					selected_model.y = selectedModel.position.y;
					selected_model.z = selectedModel.position.z;
				}
			
			}
			break;
		
		}
		case 1:{//add mode
			//http://stackoverflow.com/questions/3234256/find-mouse-position-relative-to-element
	
		
			mouse.set( ( x / div_width ) * 2 - 1, - ( y / div_height ) * 2 + 1 );

			raycaster.setFromCamera( mouse, camera );

			//threejs raycast click detection not working on loaded 3dObject
			//You need to pass the recursive flag like so:var intersects = raycaster.intersectObjects( objects, true );
			//var intersects = raycaster.intersectObjects( objects, true );	
			//var intersects = raycaster.intersectObjects( [plane], true );
			var intersects = raycaster.intersectObjects( intersectObjects, true );
			if ( intersects.length > 0 )
			{

				current_object.position.x = intersects[0].point.x;
				current_object.position.y = intersects[0].point.y;
				current_object.position.z = intersects[0].point.z;

			}
			break;
		}
		
	}
}

function onDocumentMouseUp( event ) 
{
	if (isShiftDown)
		return;
	switch(mode_index)
	{
		case 0:{//select  -- release selected object
			
			//log action
			if (selectedModel != null)
			{
				$('#btn_undo_action').removeClass('disabled');
				actions.push({	'action': 'MOVE', 
								'object_id': selectedModel.name, 
								'old_value': temp_variable, 
								'new_value': {'x': selectedModel.position.x, 'y': selectedModel.position.y, 'z': selectedModel.position.z}});
			}
			
			isSelect = false;
			selectedModel = null;
			break;
		}
	}
}
function onDocumentMouseDown( event )
{
	if (isShiftDown)
		return;
	//event.preventDefault(); // this will stop dropdown list working, because all the click function will be prevented include click dropdownlist
	//mouse.set( ( event.clientX / window.innerWidth ) * 2 - 1, - ( event.clientY / window.innerHeight ) * 2 + 1 );
	var x = event.pageX - $('#ModelWindow').offset().left;
	var y = event.pageY - $('#ModelWindow').offset().top;
	var div_width =document.getElementById("ModelWindow").clientWidth;
	var div_height=document.getElementById("ModelWindow").clientHeight;
	mouse.set( ( x / div_width ) * 2 - 1, - ( y / div_height ) * 2 + 1 );

	raycaster.setFromCamera( mouse, camera );

		switch(mode_index){
			case 0:{//select
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != controlling_scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}

					//operation
					selectedModel = controlling_scene.getObjectByName(obj.name);
					temp_variable = {'x': selectedModel.position.x, 'y': selectedModel.position.y, 'z': selectedModel.position.z};
					isSelect = true;
				}
				break;
			}
			case 1:{//add
				var intersects = raycaster.intersectObjects( [plane], true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];

					var temp_object=current_object.clone();
					temp_object.name = "model_" + generate_random_string(50);

					controlling_scene.add( temp_object );
					objects.push(temp_object);
					sceneObjects[temp_object.name]={'id': temp_object.name, 
													'directory': current_object.addition_information.directory,
													'original_filename': current_object.addition_information.original_filename,
													'file_type': current_object.addition_information.file_type,
													'x': temp_object.position.x,
													"y": temp_object.position.y,   
													"z": temp_object.position.z, 
													"size": temp_object.scale.x,     
													"rotate_x": temp_object.rotation.x,
													"rotate_y": temp_object.rotation.y,
													"rotate_z": temp_object.rotation.z};
					
					// log the add model action
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'ADD_MODEL', 
						'object_id': temp_object.name, 
						'old_value': '', 
						'new_value': {'scene_object': temp_object, 'object': sceneObjects[temp_object.name]}});
				}
				break;
			}
			case 2:{//delete mode
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != controlling_scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}

					// log the add model action
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'DELETE_MODEL', 
						'object_id': obj.name, 
						'old_value': {'scene_object': controlling_scene.getObjectByName(obj.name), 'object': sceneObjects[obj.name]}, 
						'new_value': ''});
					
					delete sceneObjects[obj.name];
					controlling_scene.remove( controlling_scene.getObjectByName(obj.name) );
					objects.splice( objects.indexOf( obj ), 1 );
					
				}
				
				break;
			}
			case 3:{//Enlarge mode
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != controlling_scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					
					var old_scale = controlling_scene.getObjectByName(obj.name).scale.x;
					
					controlling_scene.getObjectByName(obj.name).scale.multiplyScalar( 1.05 );
					sceneObjects[obj.name].size = controlling_scene.getObjectByName(obj.name).scale.x;
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'RESIZE_MODEL', 
						'object_id': obj.name, 
						'old_value': old_scale, 
						'new_value': controlling_scene.getObjectByName(obj.name).scale.x});
				}
				break;
			}
			case 4:{//reduce
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != controlling_scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					var old_scale = controlling_scene.getObjectByName(obj.name).scale.x;
					
					controlling_scene.getObjectByName(obj.name).scale.divideScalar( 1.05 );
					sceneObjects[obj.name].size = controlling_scene.getObjectByName(obj.name).scale.x;
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'RESIZE_MODEL', 
						'object_id': obj.name, 
						'old_value': old_scale, 
						'new_value': controlling_scene.getObjectByName(obj.name).scale.x});
				}
				break;
			}
			case 5:{//rotate left
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != controlling_scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					var old_value = {'x': controlling_scene.getObjectByName(obj.name).rotation.x, 
							'y': controlling_scene.getObjectByName(obj.name).rotation.y, 
							'z': controlling_scene.getObjectByName(obj.name).rotation.z};
					
					controlling_scene.getObjectByName(obj.name).rotateOnAxis(new THREE.Vector3(0,1,0), Math.PI/2/16);
					sceneObjects[obj.name].rotate_x = controlling_scene.getObjectByName(obj.name).rotation.x;
					sceneObjects[obj.name].rotate_y = controlling_scene.getObjectByName(obj.name).rotation.y;
					sceneObjects[obj.name].rotate_z = controlling_scene.getObjectByName(obj.name).rotation.z;
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'ROTATE_MODEL', 
						'object_id': obj.name, 
						'old_value': old_value, 
						'new_value': {'x': controlling_scene.getObjectByName(obj.name).rotation.x, 
									'y': controlling_scene.getObjectByName(obj.name).rotation.y, 
									'z': controlling_scene.getObjectByName(obj.name).rotation.z}});
				}
				break;
			}
			case 6:{//rotate right
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != controlling_scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					var old_value = {'x': controlling_scene.getObjectByName(obj.name).rotation.x, 
							'y': controlling_scene.getObjectByName(obj.name).rotation.y, 
							'z': controlling_scene.getObjectByName(obj.name).rotation.z};
					
					controlling_scene.getObjectByName(obj.name).rotateOnAxis(new THREE.Vector3(0,1,0), -Math.PI/2/16);
					sceneObjects[obj.name].rotate_x = controlling_scene.getObjectByName(obj.name).rotation.x;
					sceneObjects[obj.name].rotate_y = controlling_scene.getObjectByName(obj.name).rotation.y;
					sceneObjects[obj.name].rotate_z = controlling_scene.getObjectByName(obj.name).rotation.z;
					$('#btn_undo_action').removeClass('disabled');
					actions.push({	'action': 'ROTATE_MODEL', 
						'object_id': obj.name, 
						'old_value': old_value, 
						'new_value': {'x': controlling_scene.getObjectByName(obj.name).rotation.x, 
									'y': controlling_scene.getObjectByName(obj.name).rotation.y, 
									'z': controlling_scene.getObjectByName(obj.name).rotation.z}});
				}
				break;
			}

		}
		
		render();
	
}
			
function enlarge_scenario()
{
    // define new value
	var old_value = WORLD_SIZE;
    WORLD_SIZE += 100;
    controlling_scene.world_size = WORLD_SIZE;
    redraw_scenario_ground(controlling_scene);
    $('#btn_undo_action').removeClass('disabled');
    actions.push({	'action': 'RESIZE_SCENE', 
		'object_id': 'scene', 
		'old_value': old_value, 
		'new_value': WORLD_SIZE});
}

function shrink_scenario()
{
	if (WORLD_SIZE <= 0)
		return;
	var old_value = WORLD_SIZE;
    // define new value
    WORLD_SIZE -= 100;
    controlling_scene.world_size = WORLD_SIZE;
    redraw_scenario_ground(controlling_scene);
    $('#btn_undo_action').removeClass('disabled');
    actions.push({	'action': 'RESIZE_SCENE', 
		'object_id': 'scene', 
		'old_value': old_value, 
		'new_value': WORLD_SIZE});
}

function get_screen_width(){return window.screen.availWidth;}
function get_screen_height(){return window.screen.availHeight;}

function onWindowResize()
{
	
	var windowRatio = document.getElementById(scenario_element).offsetWidth/document.getElementById(scenario_element).offsetHeight;
	var windowWidth = document.getElementById(scenario_element).offsetWidth;
	var windowHeight = document.getElementById(scenario_element).offsetHeight;
	
	//camera.aspect = window.innerWidth / window.innerHeight;
	controlling_camera.aspect = windowRatio;
	controlling_camera.updateProjectionMatrix();

	//renderer.setSize( window.innerWidth, window.innerHeight );
	
	controlling_renderer.setSize( 	windowWidth,
						windowHeight
	);
}

function full_screen()
{
    if( THREEx.FullScreen.activated() )
	{
		THREEx.FullScreen.cancel();
	}
	else
	{
		old_width = $('#' + fullscreen_element).width();
		old_height = $('#' + fullscreen_element).height();
		old_control_window_height = $('#' + scenario_element).height();
		$('#' + fullscreen_element).width(SCREEN_WIDTH);
		$('#' + fullscreen_element).height(SCREEN_HEIGHT);
		
		$('#' + scenario_element).height(SCREEN_HEIGHT - $('#available_building_models').height() + 5);
		$('#' + control_element).height(SCREEN_HEIGHT - $('#available_building_models').height() + 5);
		
		onWindowResize();
		THREEx.FullScreen.request(document.getElementById(fullscreen_element));
	}
}

// full screen region
if (document.addEventListener)
{
    document.addEventListener('webkitfullscreenchange', exitHandler, false);
    document.addEventListener('mozfullscreenchange', exitHandler, false);
    document.addEventListener('fullscreenchange', exitHandler, false);
    document.addEventListener('MSFullscreenChange', exitHandler, false);
}

function exitHandler()
{
    if (document.webkitIsFullScreen || document.mozFullScreen || document.msFullscreenElement !== null)
    {
    	// change screen to fit fullscreen
    	if (!is_fullscreen) // change state from normal to fullscreen
    	{
    		
    		
    	}
    	else // change state from fullscreen to normal
    	{
    		$('#' + fullscreen_element).width(old_width);
    		$('#' + fullscreen_element).height(old_height);
    		$('#' + scenario_element).height(old_control_window_height);
    		$('#' + control_element).height(old_control_window_height);
    		onWindowResize();
    	}
    	
    	is_fullscreen = !is_fullscreen;
    }
}