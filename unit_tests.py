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
    def test_login_success(self):
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

    # 13 test create journal with normal account
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
            self.client.post('users/login/', data={'email': '412443823@qq.com', 'password': 'Zjj19911031'})
            self.client.post('admin/create_journal/', data=input_data)
            journal = Journal.query.filter_by(content=input_data['content']).first()
            # self.assertEqual(journal, None)


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
        input_data = {
            "category_id" : "4",
            "is_activate" : "y",
            "title" : "play_normal",
            "content" : "play games asdaas normal",
            "title_fi" : "Mita Kuulu asdasd",
            "content_fi" : "Hyva asdasd",
            "title_en" : "aaaaaa weq",
            "content_en" : "bbbbbbbbb asdxz",
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/create_journal/', data=input_data)
            journal = Journal.query.filter_by(title=input_data['title'], content=input_data['content']).first()
            # self.assertEqual(journal, None)

    # 17 update user info, doesn't work properly
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


    # 18 Admin update user group, doesn't work properly
    def test_update_usergroup_admin(self):
        input_data = {
            "user_id" : "12",
            "groups_value" : "|2|1|"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/update_user_info/', data=input_data)
            user = Group.query.filter_by(id=input_data['user_id']).first()
            self.assertNotEqual(user, None)


    # 19 create scenario
    def test_create_scenario(self):
        input_data = {
            "addition_information"
            "name" : "blabalascenario",
            "description" : "this is a testing scenario",
            "is_public" : "1"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('users/add_scenario/', data=input_data)
            scenario = Scenario.query.filter_by(description=input_data['name']).first()
            self.assertNotEqual(scenario, None)

    # 20 create scenario with blank title
    def test_create_scenario_blanktitle(self):
        input_data = {
            "addition_information"
            "description" : "this is a testing scenario for blank title",
            "is_public" : "1"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('users/add_scenario/', data=input_data)
            scenario = Scenario.query.filter_by(description=input_data['name']).first()
            self.assertEqual(scenario, None)


    # 21 Ban a user, failed test case
    def test_banuser(self):
        input_data={
            "user_id" : "13",
            "banned" : "1"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/update_user_info/', data=input_data)


    # 22 Unban a user
    def test_unbanuser(self):
        input_data={
            "user_id" : "13",
            "banned" : "0"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('admin/update_user_info/', data=input_data)
            self.client.post('users/login/', data={'email': 'zhoujunjie.10@gmail.com', 'password': 'Zjj19911031'})

    # 23 test add comment on scenario
    def test_addcomment_on_scenario(self):
        input_data={
            "comment_type":"scenario",
            "object_id": "mf5L9uDLCOvsDnCEEHg0na197o1ZhPD7ct3TUQZLyKe2bBBisL",
            "content" : "this is supposed to be good"
        }
        with app.app_context():
            self.client.post('users/login/', data={'email': 'df.thangld@hotmail.com', 'password': 'abc'})
            self.client.post('users/add_comment/', data=input_data)


if __name__ == '__main__':
    unittest.main()