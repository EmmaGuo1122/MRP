from flask_login import current_user
from utils.db_utilities import db
import datetime

class ActivityCategory(db.Model):

    __tablename__ = 'activity_category'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100))
    description = db.Column(db.String(200))
    alert_level = db.Column(db.String(50))
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #creator = db.relationship('User', foreign_keys=[created_by])
    created_on = db.Column(db.String(100))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #updater = db.relationship('User', foreign_keys=[updated_by])
    updated_on = db.Column(db.String(100))

    def __init__(self, id, code, description, alert_level):
        self.id = id
        self.code = code
        self.description = description
        self.alert_level = alert_level
        self.created_by = current_user.id
        self.updated_by = current_user.id
        self.created_on = datetime.datetime.now().isoformat()
        self.updated_on = datetime.datetime.now().isoformat()
    
    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'alert_level': self.alert_level,
            'displayed_name': self.code + ': ' + self.description
            #'created_by': self.creator.serialize() if self.creator else {},
            #'created_on': self.created_on,
            #'updated_by': self.updater.serialize() if self.updater else {},
            #'updated_on': self.updated_on
        }
