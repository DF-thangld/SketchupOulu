// constants
var TRIM_SCREEN_VALUE = 7;

// required variables
var fullscreen_element = 'ModelWindow';
var scenario_element = 'ModelWindow';
var controlling_scene = null;
var controlling_renderer = null;
var controlling_camera = null;
var control = null;

//variables
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
	window.addEventListener( 'resize', onWindowResize, false );
});

function animate() 
{
	requestAnimationFrame( animate );
	if (mouse_on_model || is_fullscreen)
	{
		control.enabled = true;
		control.update();
	}
	else
		control.enabled = false;
	render();
}

function render() 
{
	renderer.render( controlling_scene, controlling_camera );
}

function onWindowResize()
{
	
	var windowRatio = document.getElementById(scenario_element).offsetWidth/document.getElementById(scenario_element).offsetHeight;
	var windowWidth = document.getElementById(scenario_element).offsetWidth;
	var windowHeight = document.getElementById(scenario_element).offsetHeight;
	
	//camera.aspect = window.innerWidth / window.innerHeight;
	camera.aspect = windowRatio;
	camera.updateProjectionMatrix();

	//renderer.setSize( window.innerWidth, window.innerHeight );
	
	renderer.setSize( 	windowWidth,
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
    		$('#' + fullscreen_element).width(get_screen_width());
    		$('#' + fullscreen_element).height(get_screen_height());
    		onWindowResize();
    	}
    	else // change state from fullscreen to normal
    	{
    		$('#' + fullscreen_element).width(old_width);
    		$('#' + fullscreen_element).height(old_height);
    		console.log($('#' + fullscreen_element).width(), $('#' + fullscreen_element).height());
    		onWindowResize();
    	}
    	
    	is_fullscreen = !is_fullscreen;
    }
}