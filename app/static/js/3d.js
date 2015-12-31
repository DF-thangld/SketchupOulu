"use strict";

var file = './collada/Church.dae'; // Pfad zum Collada-Modell
var tilted = true; // Modell um 90 Grad drehen?
var modelScale = 0.1; // abhängig von der Größe des Modells
var cameraPositionZ = 1500; // Abstand der Kamera
var cameraInitialVector = 30; // field of view
var colorLight = [0xffffaa, 0xffffaa]; // Farben der beiden Lichter
var colorBackground = 0xCCFFCC; // background color
var dimensions = [window.innerWidth, window.innerHeight]; // used for aspect ratio
var canvasid = 'threedmodell'; // Name des Canvas-Containers
var rotate = [0.0005, 0.01, 0.0005]; // Geschwindigkeit der Animation (X-, Y-, Z-Achse)
var rotateManual = 0.1; // manuelle Drehung per Tastatur
var cameraZoom = 50; // manually change the zoom level
var play = false; // animate immediately after loading?
// ab hier nichts ändern

var camera, scene, renderer, dae, skin, lastFrame;
window.addEventListener('load', function() {
	if (!Detector.webgl) Detector.addGetWebGLMessage(); // Browser can support WebGL

	//--------------Initial--------------------

	scene = new THREE.Scene(); // initiated the scene

	// Camera
	camera = new THREE.PerspectiveCamera(cameraInitialVector, dimensions[0]/dimensions[1], 1, 10000); //near clipping plane :1,and far clipping plane 10000
	camera.position.z = cameraPositionZ;

	// Light
	var directionalLight1 = new THREE.DirectionalLight(colorLight[0], 1.0);
	directionalLight1.position.set(1, 0, 0);
	var directionalLight2 = new THREE.DirectionalLight(colorLight[1], 2.0);
	directionalLight2.position.set(-1, 0, 0);
	scene.add(directionalLight1);
	scene.add(directionalLight2);

	// Renderer
	renderer = new THREE.WebGLRenderer({antialias: true});
	renderer.setClearColor(colorBackground);
	renderer.setSize(dimensions[0], dimensions[1]);
	// add the renderer element to our HTML document. This is a <canvas> element the renderer uses to display the scene to us.
	renderer.setSize(1050,459);
	document.getElementById(canvasid).appendChild(renderer.domElement);

	//----------Load Collada-Modell------------

	var ModelsArray = Communicator.getModelsFromDB("Project's name");

	for (var i = 0; i < ModelsArray.length; i++) {
		var loader = new THREE.ColladaLoader();
		if (tilted) loader.options.upAxis = 'X'; // Rotation by 90 degrees
		loader.options.convertUpAxis = true; // Align the Y-axis

		var model = ModelsArray[i];
		loader.load( model.modelPath, function (collada) {
			dae = collada.scene;
			dae.scale.x = dae.scale.y = dae.scale.z = modelScale;
			dae.position.x = model.position_x;
			dae.position.y = model.position_y;
			dae.rotation.x += rotateManual*3;
			scene.add(dae);
		});
	}
	// // second
	// var loader = new THREE.ColladaLoader();
	// if (tilted) loader.options.upAxis = 'X'; // Rotation by 90 degrees
	// loader.options.convertUpAxis = true; // Align the Y-axis
	// loader.load('./collada/Building.dae', function (collada) {
	// 	dae = collada.scene;
	// 	dae.scale.x = dae.scale.y = dae.scale.z = modelScale;
	// 	dae.position.x = 200;
	// 	dae.rotation.x += rotateManual*3;
	// 	scene.add(dae);
	// });
	// //church
	// loader = new THREE.ColladaLoader();
	// if (tilted) loader.options.upAxis = 'X'; // Rotation by 90 degrees
	// loader.options.convertUpAxis = true; // Align the Y-axis
	// loader.load(file, function (collada) {
	// 	var dae = collada.scene;
	// 	dae.scale.x = dae.scale.y = dae.scale.z = modelScale;
	// 	dae.position.x = -200;
	// 	dae.rotation.x += rotateManual*3;
	// 	scene.add(dae);
	// });
	

	function render() {
		requestAnimationFrame( render );
		renderer.render( scene, camera );
	}
	render();

	// listen to keyboard
	window.addEventListener('keydown', function(e) {
		var key = e.keyCode;
		console.log("Key " + key);
		switch (key) {
			case 37: // left
				dae.rotation.y -= rotateManual;
				e.preventDefault();
				break;
			case 39: // right
				dae.rotation.y += rotateManual;
				e.preventDefault();
				break;
			case 38: // up
				dae.rotation.x -= rotateManual;
				e.preventDefault();
				break;
			case 40: // down
				dae.rotation.x += rotateManual;
				e.preventDefault();
				break;
			case 33: // pageup
				dae.rotation.z += rotateManual;
				e.preventDefault();
				break;
			case 34: // pagedown
				dae.rotation.z -= rotateManual;
				e.preventDefault();
				break;
			case 32: // space
				play = play? false : true;
				e.preventDefault();
				break;
			case 36: // home
				camera.position.z -= cameraZoom;
				e.preventDefault();
				break;
			case 35: // end
				camera.position.z += cameraZoom;
				e.preventDefault();
				break;
		}
		renderer.render(scene, camera);
	}, false);
}, false);
