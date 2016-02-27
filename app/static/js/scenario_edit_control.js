// constants
var TRIM_SCREEN_VALUE = 7;

// required variables
var fullscreen_element = 'fullscreen_area';
var scenario_element = 'ModelWindow';
var controlling_scene = null;
var controlling_renderer = null;
var controlling_camera = null;
var control = null;


// variables
var mode_index = -1;
var actions = [];
var redo_actions = [];
var temp_variable = null;
var is_fullscreen = false;
var old_width = 0;
var old_height = 0;
var current_width = 0;
var current_height = 0;
var mouse_on_model = false;

var isShiftDown = false;
var isControlDown = false;

function get_screen_width(){return window.innerWidth - TRIM_SCREEN_VALUE;}
function get_screen_height(){return window.innerHeight - TRIM_SCREEN_VALUE;}


$( document ).ready(function()
{
	$('#ModelWindow').hover(function(){mouse_on_model = true;},function(){mouse_on_model = false;});
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
	renderer.render( controlling_scene, controlling_camera );
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
				});
}

function switchMode(i)
{
	var mode = parseInt(i);
	if(mode_index ==1 && mode!=1){// from 0 to other
		current_object.visible=false;
	}else if(mode_index !=1 && mode==1){
		current_object.visible=true;
	}
	mode_index= mode ;
	switch(mode_index){
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
		case 8:{
			
			if(IsOnTop){
				//change to build on ground mode
				IsOnTop=false;
				intersectObjects=[plane];
				document.getElementById("buildWhere").innerHTML="Build On Top";
			}else{
				//change to build on top mode
				IsOnTop=true;
				intersectObjects=objects;
				document.getElementById("buildWhere").innerHTML="Build On Ground";
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



$( document ).ready(function()
{
	document.addEventListener( 'keydown', onDocumentKeyDown, false );
	document.addEventListener( 'keyup', onDocumentKeyUp, false );
	window.addEventListener( 'resize', onWindowResize, false );
	// add mouse events to mode
	document.addEventListener( 'mousemove', onDocumentMouseMove, false );
	document.addEventListener( 'mousedown', onDocumentMouseDown, false );
	document.addEventListener( 'mouseup', onDocumentMouseUp, false );
});


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
		case 83: move_down = true; break; // s
		case 90: is_rotating = true; break; // z
		case 70 : // f
			if ((mouse_on_model || is_fullscreen) && isControlDown)
			{
				if( THREEx.FullScreen.activated() )
				{
					THREEx.FullScreen.cancel();
				}
				else
				{
					THREEx.FullScreen.request(document.getElementById(fullscreen_element));
				}
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

function onDocumentMouseUp( event ) {
	switch(mode_index)
	{
		case 0:{//select  -- release selected object
			
			//log action
			if (selectedModel != null)
				actions.push({	'action': 'MOVE', 
								'object_id': selectedModel.name, 
								'old_value': temp_variable, 
								'new_value': {'x': selectedModel.position.x, 'y': selectedModel.position.y, 'z': selectedModel.position.z}});
			
			isSelect = false;
			selectedModel = null;
			break;
		}
	}
}
function onDocumentMouseDown( event )
{
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
					
					controlling_scene.getObjectByName(obj.name).scale.multiplyScalar( 1.2 );
					sceneObjects[obj.name].size = controlling_scene.getObjectByName(obj.name).scale.x;
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
					
					controlling_scene.getObjectByName(obj.name).scale.divideScalar( 1.2 );
					sceneObjects[obj.name].size = controlling_scene.getObjectByName(obj.name).scale.x;
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
					
					controlling_scene.getObjectByName(obj.name).rotateOnAxis(new THREE.Vector3(0,1,0), Math.PI/2/4);
					sceneObjects[obj.name].rotate_x = controlling_scene.getObjectByName(obj.name).rotation.x;
					sceneObjects[obj.name].rotate_y = controlling_scene.getObjectByName(obj.name).rotation.y;
					sceneObjects[obj.name].rotate_z = controlling_scene.getObjectByName(obj.name).rotation.z;
					
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
					
					controlling_scene.getObjectByName(obj.name).rotateOnAxis(new THREE.Vector3(0,1,0), -Math.PI/2/4);
					sceneObjects[obj.name].rotate_x = controlling_scene.getObjectByName(obj.name).rotation.x;
					sceneObjects[obj.name].rotate_y = controlling_scene.getObjectByName(obj.name).rotation.y;
					sceneObjects[obj.name].rotate_z = controlling_scene.getObjectByName(obj.name).rotation.z;
					
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
    actions.push({	'action': 'RESIZE_SCENE', 
		'object_id': 'scene', 
		'old_value': old_value, 
		'new_value': WORLD_SIZE});
}



function onWindowResize()
{
	
	var windowRatio = document.getElementById("ModelWindow").offsetWidth/document.getElementById("ModelWindow").offsetHeight;
	var windowWidth = document.getElementById("ModelWindow").offsetWidth;
	var windowHeight = document.getElementById("ModelWindow").offsetHeight;
	
	//camera.aspect = window.innerWidth / window.innerHeight;
	camera.aspect = windowRatio;
	camera.updateProjectionMatrix();

	//renderer.setSize( window.innerWidth, window.innerHeight );
	
	renderer.setSize( 	windowWidth,
						windowHeight
	);
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
    	/*if (!is_fullscreen) // change state from normal to fullscreen
    	{
    		old_width = $('#' + fullscreen_element).width();
    		old_height = $('#' + fullscreen_element).height();
    		$('#' + fullscreen_element).width(get_screen_width());
    		$('#' + fullscreen_element).height(get_screen_height());
    	}
    	else // change state from fullscreen to normal
    	{
    		$('#' + fullscreen_element).width(old_width);
    		$('#' + fullscreen_element).height(old_height);
    		console.log($('#' + fullscreen_element).width(), $('#' + fullscreen_element).height());
    	}*/
    	
    	is_fullscreen = !is_fullscreen;
    }
}