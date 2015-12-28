from flask import Flask, request, Response, g, jsonify, Response
from flask.ext import restful
from flask.ext.restful import reqparse, abort, Api, Resource
import json
import sqlite3
from models.scenario import Scenario

class BaseScenarios(restful.Resource):

    def get(self):
        
        base_scenarios = Scenario.query.filter_by(is_base_scenario=True).all()
        
        return Response(json.dumps(base_scenarios), 200, mimetype='application/hal+json')