/**
 * @author Pingjiang Li lpj614@hotmail.com
 */

var Communicator = {

	getModelsFromDB: function (parameters) {

	var model_0= {
		modelName:"Church",
		modelPath:'./collada/Church.dae',
		position_x:-200,
		position_y:0,
	};
	var model_1= {
		modelName:"Building",
		modelPath:'./collada/Building.dae',
		position_x:200,
		position_y:0,
	}; 
	var model_2= {
		modelName:"Church",
		modelPath:'./collada/Church.dae',
		position_x:-200,
		position_y:0,
	};

	var ModelsArray = [];
	ModelsArray[0]=model_0;
	ModelsArray[1]=model_1;
	//ModelsArray[1]=model_2;

	return ModelsArray;

	},

	updateModelsToDB: function ( parameters ) {

	}

};