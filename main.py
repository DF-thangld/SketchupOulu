from variables import app, db
from restful_resources.base_scenario import BaseScenarios
from flask.ext import restful
from flask.ext.cors import CORS

api = restful.Api(app)
cors = CORS(app)

api.add_resource(BaseScenarios, '/api/base_scenarios')

if __name__ == '__main__':
    app.run(debug=True)