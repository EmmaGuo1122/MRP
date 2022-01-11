from utils.db_utilities import db
from flask_login import current_user
from utils import prj_constants
import datetime

class Tenant(db.Model):

    __tablename__ = 'tenant'

    id = db.Column(db.Integer, primary_key=True)
    unique_name = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    site = db.relationship('Site', foreign_keys=[site_id])
    status = db.Column(db.String(50))
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #creator = db.relationship('User', foreign_keys=[created_by])
    created_on = db.Column(db.String(100))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #updater = db.relationship('User', foreign_keys=[updated_by])
    updated_on = db.Column(db.String(100))

    def __init__(self, id, unique_name, unit, site_id):
        self.id = id
        self.unique_name = unique_name
        self.unit = unit
        self.site_id = site_id
        self.status = prj_constants.TENANT_STATUS_ACTIVE
        self.created_by = current_user.id
        self.updated_by = current_user.id
        self.created_on = datetime.datetime.now().isoformat()
        self.updated_on = datetime.datetime.now().isoformat()
    
    def serialize(self):
        return {
            'id': self.id,
            'unique_name': self.unique_name,
            'unit': self.unit,
            'site': self.site.serialize() if self.site else {},
            'site_id': self.site_id,
            'site_name': self.site.name if self.site else None,
            'status': self.status
            #'created_by': self.creator.serialize() if self.creator else {},
            #'created_on': self.created_on,
            #'updated_by': self.updater.serialize() if self.updater else {},
            #'updated_on': self.updated_on
        }
