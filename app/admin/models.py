from app import db
import config

class SystemParameter(db.Model):
    
    __tablename__ = 'system_parameters'
    name = db.Column(db.String(200), primary_key=True)
    value = db.Column(db.String(200))