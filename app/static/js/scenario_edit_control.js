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

$('#ModelWindow').hover(function(){mouse_on_model = true;},function(){mouse_on_model = false;});


function animate() 
{
	requestAnimationFrame( animate );
	if (isShiftDown)
	{
		control.update();
		var metric= Math.ceil( controlling_camera.position.y/10 );
    	document.getElementById("metric").innerHTML=metric +"m";
	}
	render();
}

function render() 
{
	for (i=0; i < building_models.length; i++)
    {
        var building_model = building_models[i];
        building_model['renderer'].render( building_model['scene'], building_model['camera'] );
    }
	renderer.render( scene, camera );
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

document.addEventListener( 'keydown', onDocumentKeyDown, false );
document.addEventListener( 'keyup', onDocumentKeyUp, false );
window.addEventListener( 'resize', onWindowResize, false );
// add mouse events to mode
document.addEventListener( 'mousemove', onDocumentMouseMove, false );
document.addEventListener( 'mousedown', onDocumentMouseDown, false );
document.addEventListener( 'mouseup', onDocumentMouseUp, false );

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
	if (mouse_on_model)
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
	switch(mode_index){
		case 0:{//select  -- release selected object
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
					while( obj.parent != scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}

					//operation
					selectedModel = scene.getObjectByName(obj.name);
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

					scene.add( temp_object );
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
				}
				break;
			}
			case 2:{//delete mode
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}

					delete sceneObjects[obj.name];
					scene.remove( scene.getObjectByName(obj.name) );
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
					while( obj.parent != scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					
					scene.getObjectByName(obj.name).scale.multiplyScalar( 1.2 );
					sceneObjects[obj.name].size = scene.getObjectByName(obj.name).scale.x;
					console.log(sceneObjects[obj.name]);
				}
				break;
			}
			case 4:{//reduce
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					
					scene.getObjectByName(obj.name).scale.divideScalar( 1.2 );
					sceneObjects[obj.name].size = scene.getObjectByName(obj.name).scale.x;
					console.log(sceneObjects[obj.name]);
				}
				break;
			}
			case 5:{//rotate left
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					
					scene.getObjectByName(obj.name).rotateOnAxis(new THREE.Vector3(0,1,0), Math.PI/2/4);
					sceneObjects[obj.name].rotate_x = scene.getObjectByName(obj.name).rotation.x;
					sceneObjects[obj.name].rotate_y = scene.getObjectByName(obj.name).rotation.y;
					sceneObjects[obj.name].rotate_z = scene.getObjectByName(obj.name).rotation.z;
				}
				break;
			}
			case 6:{//rotate right
				var intersects = raycaster.intersectObjects( objects, true );
				if ( intersects.length > 0 ) {
					var intersect = intersects[ 0 ];
					var obj=intersect.object;
					obj.name;
					while( obj.parent != scene && obj.parent!=null ){
						obj = obj.parent;
						obj.name;
					}
					
					scene.getObjectByName(obj.name).rotateOnAxis(new THREE.Vector3(0,1,0), -Math.PI/2/4);
					sceneObjects[obj.name].rotate_x = scene.getObjectByName(obj.name).rotation.x;
					sceneObjects[obj.name].rotate_y = scene.getObjectByName(obj.name).rotation.y;
					sceneObjects[obj.name].rotate_z = scene.getObjectByName(obj.name).rotation.z;
				}
				break;
			}

		}
		
		render();
	
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