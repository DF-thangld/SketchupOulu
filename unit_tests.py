import unittest
from flask import Flask, g, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.testing import TestCase


from app import app
from app.users.models import User

class SketchupOuluUnitTest(TestCase):

    def create_app(self):
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        with app.app_context():
            g.user = None

    def login(self, email, password):
	
		input_data = {
            "email": email,
            "password": password
        }
        with app.app_context():
            resp = self.client.post('users/login', data=input_data, follow_redirects=True)

    def logout(self):
		with app.app_context():
            resp = self.client.post('users/logout', data=input_data, follow_redirects=True)
		
	def login_as_admin(self):
		self.login('df.thangld@hotmail.com', 'abc')
		
	def login_as_user(self):
		self.login('dreamingfighter@gmail.com', 'abc')

    def test_login_sucess(self):
        input_data = {
            "email": "df.thangld@hotmail.com",
            "password": "abc"
        }
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertIn('user', g)
            self.assertNotEqual(g.user, None)

    def test_login_unsucessful(self):
        input_data = {
            "email": "df.thangld@hotmail.com",
            "password": "abc1"
        }
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertNotIn('user', g)

if __name__ == '__main__':
    unittest.main()