from flask import Flask, request, Response, g, jsonify, Response
from flask.ext import restful
from flask.ext.restful import reqparse, abort, Api, Resource
import json
import sqlite3

class User(restful.Resource):
    
    @staticmethod
    def check_login(username, password):
        db = PWP33Database()
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        check_login_sql = "select * from pwp_users where user_name = ? and user_password=?"
        cur.execute(check_login_sql, (username,password))
        user_row = cur.fetchone()
        if user_row is None:
            return False
        else:
            return True

    def get(self, user_name):
        db = PWP33Database()
        user = db.get_user(user_name)
        
        if user is None:
            return Response(json.dumps({'error' : 'User not found'}), 404, mimetype='application/json')
        
        return Response (json.dumps({
            "_links" : {
                "self" : { "href" : "api/user/" + user_name},
                "all_users" : { "href" : "api/users"},
                "teams" : { "href" : "api/user/" + user_name + "/teams"}
            },
            "user_id" : user['user_id'],
            "user_name" : user_name,
            "user_full_name" : user['user_fullname'],
            "user_birth_date" : user['user_birthdate'],
            "user_email" : user['user_email']
        }), 200, mimetype='application/hal+json')
    
    def put(self, user_name):
        db = PWP33Database()
        args = request.get_json(force=True)
        try:
            user = db.get_user(user_name)
            if user is None:
                return Response(json.dumps({'error' : 'User not found'}), 404, mimetype='application/json')
            db.update_user(user_name, args['password'], args['full_name'], args['birth_date'], args['email'])
            user = db.get_user(user_name)
            return Response (json.dumps({
                "_links" : {
                    "self" : { "href" : "api/user/" + user_name},
                    "all_users" : { "href" : "api/users"},
                    "teams" : { "href" : "api/user/" + user_name + "/teams"}
                },
                "user_id" : user['user_id'],
                "user_name" : user_name,
                "user_full_name" : user['user_fullname'],
                "user_birth_date" : user['user_birthdate'],
                "user_email" : user['user_email']
            }), 200, mimetype='application/hal+json')
        except Exception as error_detail:
            return Response(json.dumps({'error' : str(error_detail)}), 422, mimetype='application/json')
    
    def delete(self, user_name):
        db = PWP33Database()
        try:
            db.delete_user(user_name)
            return Response(json.dumps({'Success' : 'true'}), 204, mimetype='application/json')
        except Exception as error_detail:
            return Response(json.dumps({'error' : str(error_detail)}), 404, mimetype='application/json')
        
    
    