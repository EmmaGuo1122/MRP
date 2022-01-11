from utils.db_utilities import db
from flask_login import current_user
import datetime

class NotificationEmail(db.Model):

    __tablename__ = 'site_notification_email'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    notification_email = db.Column(db.String(100))
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #creator = db.relationship('User', foreign_keys=[created_by])
    created_on = db.Column(db.String(100))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #updater = db.relationship('User', foreign_keys=[updated_by])
    updated_on = db.Column(db.String(100))

    def __init__(self, id, site_id, notification_email):
        self.id = id
        self.site_id = site_id
        self.notification_email = notification_email
        self.created_by = current_user.id
        self.updated_by = current_user.id
        self.created_on = datetime.datetime.now().isoformat()
        self.updated_on = datetime.datetime.now().isoformat()
    
    def serialize(self):
        return {
            'id': self.id,
            'site_id': self.site_id,
            'notification_email': self.notification_email
            #'created_by': self.creator.serialize() if self.creator else {},
            #'created_on': self.created_on,
            #'updated_by': self.updater.serialize() if self.updater else {},
            #'updated_on': self.updated_on
        }
