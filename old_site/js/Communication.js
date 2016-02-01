/**
 * @author Pingjiang Li lpj614@hotmail.com
 */

var Communicator = {

	getModelsFromDB: function (parameters) {

	var model_0= {
		modelName:"building_1",
		objPath:'./object/building_1/building_1.obj',
		mtlPath:'./object/building_1/building_1.mtl',
		position_x:0,
		position_y:0,
	};
	var model_1= {
		modelName:"building_2",
		objPath:'./object/building_2/building_2.obj',
		mtlPath:'./object/building_2/building_2.mtl',
		position_x:0,
		position_y:0,
	};
	var model_2= {
		modelName:"tree_1",
		objPath:'./object/tree_1/tree_1.obj',
		mtlPath:'./object/tree_1/tree_1.mtl',
		position_x:0,
		position_y:0,
	};
	var model_3= {
		modelName:"terrain_1",
		objPath:'./object/terrain_1/terrain_1.obj',
		mtlPath:'./object/terrain_1/terrain_1.mtl',
		position_x:0,
		position_y:0,
	};
	/*var model_2= {
		modelName:"Church",
		modelPath:'./collada/Church.dae',
		position_x:-200,
		position_y:0,
	};*/

	var ModelsArray = [];
	ModelsArray[0]=model_0;
	ModelsArray[1]=model_1;
	ModelsArray[2]=model_2;
	ModelsArray[3]=model_3;

	return ModelsArray;

	},
	getSceneFromDB: function (parameters) {

	var model_0= {
		modelName:"building_1",
		index:"0",
		x:0,
		y:0,
		z:0,
	};
	var model_1= {
		modelName:"building_2",
		index:"1",
		x:300,
		y:100,
		z:0,
	};
	/*var model_2= {
		modelName:"tree_1",
		objPath:'./object/tree_1/tree_1.obj',
		mtlPath:'./object/tree_1/tree_1.mtl',
		position_x:0,
		position_y:0,
	};
	var model_3= {
		modelName:"terrain_1",
		objPath:'./object/terrain_1/terrain_1.obj',
		mtlPath:'./object/terrain_1/terrain_1.mtl',
		position_x:0,
		position_y:0,
	};
	var model_2= {
		modelName:"Church",
		modelPath:'./collada/Church.dae',
		position_x:-200,
		position_y:0,
	};*/

	var ModelsArray = [];
	ModelsArray[0]=model_0;
	ModelsArray[1]=model_1;
	//ModelsArray[2]=model_2;
	//ModelsArray[3]=model_3;

	return ModelsArray;

	},

	updateModelsToDB: function ( parameters ) {

	}

};