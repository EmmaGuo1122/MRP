from flask_login import current_user
from utils.db_utilities import db
from utils import string_utilities
import datetime

class ActivityTracking(db.Model):

    __tablename__ = 'activity_tracking'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    site = db.relationship('Site', foreign_keys=[site_id])
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    tenant = db.relationship('Tenant', foreign_keys=[tenant_id])
    activity_category_id = db.Column(db.Integer, db.ForeignKey('activity_category.id'))
    activity_category = db.relationship('ActivityCategory', foreign_keys=[activity_category_id])
    date_of_record = db.Column(db.Integer)
    time_of_record = db.Column(db.Integer)
    comments = db.Column(db.String(500)) 
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #creator = db.relationship('User', foreign_keys=[created_by])
    created_on = db.Column(db.String(100))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #updater = db.relationship('User', foreign_keys=[updated_by])
    updated_on = db.Column(db.String(100))

    def __init__(self, id, site_id, tenant_id, activity_category_id, date_of_record, time_of_record, comments):
        self.id = id
        self.site_id = site_id
        self.tenant_id = tenant_id
        self.activity_category_id = activity_category_id
        self.date_of_record = date_of_record
        self.time_of_record = time_of_record
        self.comments = comments
        self.created_by = current_user.id
        self.updated_by = current_user.id
        self.created_on = datetime.datetime.now().isoformat()
        self.updated_on = datetime.datetime.now().isoformat()
    
    def serialize(self):
        return {
            'id': self.id,
            'site': self.site.serialize(),
            'site_id': self.site_id,
            'site_name': self.site.name,
            'tenant': self.tenant.serialize(),
            'tenant_id': self.tenant_id,
            'tenant_name': self.tenant.unique_name,
            'activity_category': self.activity_category.serialize(),
            'activity_category_id': self.activity_category_id,
            'activity_category_name': self.activity_category.code + ': ' + self.activity_category.description,
            'date_of_record': string_utilities.convert_int_to_yyyymmdd_str(self.date_of_record),
            'time_of_record': string_utilities.convert_int_to_hh24miss_str(self.time_of_record),
            'comments': self.comments
            #'created_by': self.creator.serialize() if self.creator else {},
            #'created_on': self.created_on,
            #'updated_by': self.updater.serialize() if self.updater else {},
            #'updated_on': self.updated_on
        }
