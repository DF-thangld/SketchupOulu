from app import app, db
import app.users.models as users
import app.sketchup.models as sketchup
import app.journal.models as journal
import app.admin.models as admin
print('create database schema')
db.create_all()

print('create groups')
admin_group = users.Group('Administrators', '')
admin_group.id = 1
user_group = users.Group('Public Users', '')
user_group.id = 2
db.session.add(admin_group)
db.session.add(user_group)

print('create first admin user')
user = users.User(username='admin', email=config.EMAIL['address'], password='abcxyz')
user.banned = 0
user.groups.append(admin_group)
user.groups.append(user_group)
db.session.add(user)

print ('create version tag')
version_tag = admin.SystemParameter()
version_tag.name = 'version'
version_tag.value = '1.00'
db.session.add(version_tag)

print('commit to database')
db.session.commit()
print('finish')