from utils.db_utilities import db
from flask_login import current_user
from utils import prj_constants
import datetime

class SystemConfiguration(db.Model):

    __tablename__ = 'system_configuration'

    id = db.Column(db.Integer, primary_key=True)
    conf_key = db.Column(db.String(100))
    conf_value = db.Column(db.String(100))
    validation_regex = db.Column(db.String(200))
    description = db.Column(db.String(300))
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #creator = db.relationship('User', foreign_keys=[created_by])
    created_on = db.Column(db.String(100))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #updater = db.relationship('User', foreign_keys=[updated_by])
    updated_on = db.Column(db.String(100))

    def __init__(self, id, conf_key, conf_value, validation_regex):
        self.id = id
        self.conf_key = conf_key
        self.conf_value = conf_value
        self.validation_regex = validation_regex
        self.created_by = current_user.id
        self.updated_by = current_user.id
        self.created_on = datetime.datetime.now().isoformat()
        self.updated_on = datetime.datetime.now().isoformat()
    
    def serialize(self):
        return {
            'id': self.id,
            'conf_key': self.conf_key,
            'conf_value': self.conf_value,
            'validation_regex': self.validation_regex,
            'description': self.description
            #'created_by': self.creator.serialize() if self.creator else {},
            #'created_on': self.created_on,
            #'updated_by': self.updater.serialize() if self.updater else {},
            #'updated_on': self.updated_on
        }
