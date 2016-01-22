import unittest
from flask import Flask, g, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.testing import TestCase


from app import app
from app.users.models import User

class SketchupOuluUnitTest(TestCase):

    def create_app(self):
        app.config['WTF_CSRF_ENABLED'] = False
        with app.app_context():
            g.user = None
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
            resp = self.client.post('users/logout', follow_redirects=True)
		
    def login_as_admin(self):
        with app.app_context():
            self.login('df.thangld@hotmail.com', 'abc')
		
    def login_as_user(self):
        with app.app_context():
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

    def register_successful(self):
        input_data = {
            "name" : "Junjie1991",
            "email" : "zhoujunjie.10@gmail.com",
            "password" : "1234",
            "confirm" : "1234"
            "read"
        }
        with app.app_context():
            resp = self.client.post('users/register/', data=input_data)
            user = User.query.filter_by(username=input_data['name'], email=input_data['email']).first()
            self.assertNotEqual(user, None)

    def test_login_notfound(self):
        input_data = {"email": "sadasd",
                      "password": "abc"}
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertNotIn('user', g)

    def test_login_wrongpassword(self):
        input_data = {"email": "df.thangld@hotmail.com",
            "password": "abcd"
                    }
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertNotIn('user', g)


    def test_upload_profile(self):
        input_data = {
            "address" : "Vietnam",
            "fullname" : "Luu Thang",
            "phone_number" : "12345"
        }
        with app.app_context():
            #to login, use this line of code
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            resp = self.client.post('users/user_profile/', data=input_data)
            user = User.query.filter_by(address=input_data['address']).first()
            self.assertNotEqual(user, None)





if __name__ == '__main__':
    unittest.main()