from app import db
import config

class SystemParameter(db.Model):
    
    __tablename__ = 'system_parameters'
    name = db.Column('parameter_name', db.String(200), primary_key=True)
    value = db.Column('parameter_value', db.String(200))