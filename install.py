from app import app, db
import app.users.models
import app.sketchup.models
import app.journal.models


db.create_all()
print('finish')