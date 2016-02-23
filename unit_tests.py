import unittest
from flask import Flask, g, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.testing import TestCase


from app import app
from app.users.models import User
from app.journal.models import Journal
from app.users.models import Group
from app.sketchup.models import Scenario

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

    # 1
    def test_login_sucess(self):
        input_data = {
            "email": "zhoujunjie.10@gmail.com",
            "password": "Zjj19911031"
        }
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertIn('user', g)
            self.assertNotEqual(g.user, None)

    # 2
    def test_login_unsuccessful(self):
        input_data = {
            "email": "zhoujunjie.10@gmail.com",
            "password": "Zjj199110311"
        }
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertNotIn('user', g)


    # 3
    def test_register_successful(self):
        input_data = {
            "name" : "Junjie",
            "email" : "zhoujunjie.10@gmail.com",
            "password" : "1234",
            "confirm" : "1234"
            "read"
        }
        with app.app_context():
            resp = self.client.post('users/register/', data=input_data)
            user = User.query.filter_by(username=input_data['name'], email=input_data['email']).first()
            self.assertNotEqual(user, None)

    # 4
    def test_register_unsuccessful_duplicateusername(self):
        input_data = {
            "name" : "Junjie",
            "email" : "asdasdasd23@qq.com",
            "password" : "1234",
            "confirm" : "1234"
            "read"
        }
        with app.app_context():
            resp = self.client.post('users/register/', data=input_data)
            user = User.query.filter_by(username=input_data['name'], email=input_data['email']).first()
            self.assertEqual(user, None)

    # 5
    def test_register_unsuccessful_duplicateemail(self):
        input_data = {
            "name" : "Hello",
            "email" : "412443823@qq.com",
            "password" : "1234",
            "confirm" : "1234"
            "read"
        }
        with app.app_context():
            resp = self.client.post('users/register/', data=input_data)
            user = User.query.filter_by(username=input_data['name'], email=input_data['email']).first()
            self.assertEqual(user, None)

    # 6
    def test_register_unsuccessful_misspassword(self):
        input_data = {
            "name" : "Hellobaby",
            "email" : "123asdas@qq.com",
        }
        with app.app_context():
            resp = self.client.post('users/register/', data=input_data)
            user = User.query.filter_by(username=input_data['name'], email=input_data['email']).first()
            self.assertEqual(user, None)



    # 7
    def test_login_notfound(self):
        input_data = {"email": "sadasd",
                      "password": "abc"}
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertNotIn('user', g)

    # 8
    def test_login_wrongpassword(self):
        input_data = {"email": "df.thangld@hotmail.com",
            "password": "abcd"
                    }
        with app.app_context():
            resp = self.client.post('users/login/', data=input_data)
            self.assertNotIn('user', g)


    # 9 user update profile
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


    # 10
    def test_send_email(self):
        input_data = {
            "action" : "send",
            "emails"    :  "zhoujunjie.10@gmail.com",
            "title" :   "Test send email",
            "content" : "Hello World from SketchUp Oulu",
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            resp = self.client.post('admin/send_email/', data=input_data)


    # 11
    def test_send_email_normaluser(self):
        input_data = {
            "action" : "send",
            "emails"    :  "zhoujunjie.10@gmail.com",
            "title" :   "Test send email with normal account",
            "content" : "Hello World from Junjie SketchUp Oulu",
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': '412443823@qq.com', 'password': 'Zjj19911031'})
            resp = self.client.post('admin/send_email/', data=input_data)


    # 12
    def test_create_journal_admin(self):
        input_data = {
            "category_id" : "4",
            "is_activate" : "y",
            "title" : "play",
            "content" : "play games",
            "title_fi" : "Mita Kuulu",
            "content_fi" : "Hyva",
            "title_en" : "aaaaaa",
            "content_en" : "bbbbbbbbb",
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/create_journal/', data=input_data)

    # 13
    def test_create_journal_normaluser(self):
        input_data = {
            "category_id" : "4",
            "is_activate" : "y",
            "title" : "play_normal",
            "content" : "play games normal",
            "title_fi" : "Mita Kuulu",
            "content_fi" : "Hyva",
            "title_en" : "aaaaaa",
            "content_en" : "bbbbbbbbb",
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/create_journal/', data=input_data)

    # 14
    def test_create_journal_blanktitle_admin(self):
        input_data = {
            "category_id" : "4",
            "is_activate" : "y",
            "content" : "play games hahaha",
            "title_fi" : "Mita Kuulu",
            "content_fi" : "Hyva",
            "title_en" : "aaaaaa",
            "content_en" : "bbbbbbbbb",
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/create_journal/', data=input_data)
            journal = Journal.query.filter_by(content=input_data['content']).first()
            self.assertEqual(journal, None)

    # 15
    def test_create_journal_blankcontent_admin(self):
        input_data = {
            "category_id" : "4",
            "is_activate" : "y",
            "title" : "play_normal test blank content",
            "title_fi" : "Mita Kuulu",
            "content_fi" : "Hyva",
            "title_en" : "aaaaaa",
            "content_en" : "bbbbbbbbb",
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/create_journal/', data=input_data)
            journal = Journal.query.filter_by(title=input_data['title']).first()
            self.assertEqual(journal, None)

    # 16 create journal with same title with existed one
    def test_create_journal_sametitle(self):



    # 16 update user info
    def test_update_userprofile_admin(self):
        input_data = {
            "user_id" : "13",
            "fullname": "hahahahahaha",
            "address" : "Wuxi, China",
            "phone_number" : "412443823"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/update_user_info/', data=input_data)
            user = User.query.filter_by(fullname=input_data['fullname']).first()
            self.assertNotEqual(user, None)


    # 17 Admin update user group
    def test_update_usergroup_admin(self):
        input_data = {
            "user_id" : "12",
            "groups_value" : "|2|1|"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/update_user_info/', data=input_data)
            user = Group.query.filter_by(id=input_data['groups_value']).first()
            # self.assertNotEqual(user, None)


    # 18 create scenario
    def test_create_scenario(self):
        input_data = {
            "addition_information" : {"model_THyGEE2bBwWgZdPWJy29D51CTrCNudaTauatGaZ6SHOTYVC7E9":{"id":"model_THyGEE2bBwWgZdPWJy29D51CTrCNudaTauatGaZ6SHOTYVC7E9","directory":"YgAgPaYMVdDElUwfa1ZtCjPjCKKjNREgD0amGtYJGlNqyB62AX","original_filename":"building_2","file_type":"objmtl","x":128.1677682103175,"y":0,"z":-311.52215855827365,"size":1,"rotate_x":0,"rotate_y":0,"rotate_z":0},"model_tWNuqfKnZZvrhkT6E2RDLWo2z9MpJnXPNJ0vTnEzDsrskmMvK4":{"id":"model_tWNuqfKnZZvrhkT6E2RDLWo2z9MpJnXPNJ0vTnEzDsrskmMvK4","directory":"YgAgPaYMVdDElUwfa1ZtCjPjCKKjNREgD0amGtYJGlNqyB62AX","original_filename":"building_2","file_type":"objmtl","x":2.518872265404621,"y":0,"z":-328.8096435312111,"size":1,"rotate_x":0,"rotate_y":0,"rotate_z":0},"model_TghWayJdUXJlzk0BwzpzzOKuiA1Wf7HgfLxgJWYguD52JkPDMV":{"id":"model_TghWayJdUXJlzk0BwzpzzOKuiA1Wf7HgfLxgJWYguD52JkPDMV","directory":"Ua9zdzQE1Foa70xc1fQ976vr2ac7EkiOt0rH6UZn79IHbyBOhI","original_filename":"male02","file_type":"objmtl","x":-181.51697001965312,"y":0,"z":-348.3533426561828,"size":1,"rotate_x":0,"rotate_y":0,"rotate_z":0},"size":700},
            "name" : "blabalascenario",
            "description" : "this is a testing scenario",
            "is_public" : "1"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('users/add_scenario/', data=input_data)
            scenario = Scenario.query.filter_by(name=input_data['name']).first()
            self.assertNotEqual(scenario, None)

if __name__ == '__main__':
    unittest.main()