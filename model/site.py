from utils.db_utilities import db
from flask_login import current_user
from model.notification_email import NotificationEmail
import datetime

class Site(db.Model):

    __tablename__ = 'site'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postal_code = db.Column(db.String(50))
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    manager = db.relationship('User', foreign_keys=[manager_id])
    notification_emails = db.relationship('NotificationEmail')
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #creator = db.relationship('User', foreign_keys=[created_by])
    created_on = db.Column(db.String(100))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #updater = db.relationship('User', foreign_keys=[updated_by])
    updated_on = db.Column(db.String(100))

    def __init__(self, id, name, address_line1, address_line2, city, province, postal_code, manager_id):
        self.id = id
        self.name = name
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.province = province
        self.postal_code = postal_code
        self.manager_id = manager_id
        self.created_by = current_user.id
        self.updated_by = current_user.id
        self.created_on = datetime.datetime.now().isoformat()
        self.updated_on = datetime.datetime.now().isoformat()
    
    @property
    def get_displayed_address(self):
        displayed_str = self.address_line1
        if self.address_line2:
            displayed_str += ', ' + self.address_line2
        displayed_str += ', ' + self.city
        displayed_str += ', ' + self.province
        displayed_str += ', ' + self.postal_code

        return displayed_str
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'province': self.province,
            'postal_code': self.postal_code,
            'displayed_address': self.get_displayed_address,
            'manager': self.manager.serialize() if self.manager else {},
            'manager_id': self.manager_id,
            'manager_name': self.manager.get_displayed_full_name if self.manager else None,
            'notification_emails': [e.serialize() for e in self.notification_emails]
            #'created_by': self.creator.serialize() if self.creator else {},
            #'created_on': self.created_on,
            #'updated_by': self.updater.serialize() if self.updater else {},
            #'updated_on': self.updated_on
        }
