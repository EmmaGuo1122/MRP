from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from utils.db_utilities import db
from utils import prj_constants
import datetime

class User(UserMixin, db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100)) #generate_password_hash('admin')
    email = db.Column(db.String(100))
    status = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #creator = db.relationship('User', remote_side=[id], foreign_keys=[created_by])
    created_on = db.Column(db.String(100))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    #updater = db.relationship('User', remote_side=[id], foreign_keys=[updated_by])
    updated_on = db.Column(db.String(100))

    def __init__(self, id, username, password, email, first_name, last_name, role, site_id):
        self.id = id
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email
        self.status = prj_constants.USER_STATUS_ACTIVE
        self.created_by = current_user.id
        self.updated_by = current_user.id
        self.created_on = datetime.datetime.now().isoformat()
        self.updated_on = datetime.datetime.now().isoformat()
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.site_id = site_id

    def set_password(self,password):
        self.password = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password,password)

    @property
    def get_displayed_name(self):
         return self.first_name if self.first_name else self.username

    @property
    def get_displayed_full_name(self):
        ret_str = self.username
        if self.first_name:
            ret_str = self.first_name
            ret_str += (' ' + self.last_name) if self.last_name else ''
        
        return ret_str
    
    def can_add_user(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SITE_MANAGER
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_edit_user(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SITE_MANAGER
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_delete_user(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SITE_MANAGER
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_add_site(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_edit_site(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SITE_MANAGER
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_delete_site(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_add_tenant(self):
        return True

    def can_edit_tenant(self):
        return True

    def can_delete_tenant(self):
        return True
    
    def can_access_system_configuration(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_edit_system_configuration(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )
    
    def can_add_activity_category(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_edit_activity_category(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )

    def can_delete_activity_category(self):
        return (
            self.role == prj_constants.USER_ROLE_ADMIN
            or self.role == prj_constants.USER_ROLE_SUPER_ADMIN
        )
    
    def can_add_activity_tracking(self):
        return True

    def can_edit_activity_tracking(self):
        return True

    def can_delete_activity_tracking(self):
        return True
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'status': self.status,
            #'created_by': self.creator.serialize() if self.creator else {},
            #'created_on': self.created_on,
            #'updated_by': self.updater.serialize() if self.updater else {},
            #'updated_on': self.updated_on,
            'displayed_name': self.get_displayed_name,
            'displayed_full_name': self.get_displayed_full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'site_id': self.site_id,
            'permission': {
                'can_add_user': self.can_add_user(),
                'can_edit_user': self.can_edit_user(),
                'can_delete_user': self.can_delete_user(),
                'can_add_site': self.can_add_site(),
                'can_edit_site': self.can_edit_site(),
                'can_delete_site': self.can_delete_site(),
                'can_add_tenant': self.can_add_tenant(),
                'can_edit_tenant': self.can_edit_tenant(),
                'can_delete_tenant': self.can_delete_tenant(),
                'can_access_system_configuration': self.can_access_system_configuration(),
                'can_edit_system_configuration': self.can_edit_system_configuration(),
                'can_add_activity_category': self.can_add_activity_category(),
                'can_edit_activity_category': self.can_edit_activity_category(),
                'can_delete_activity_category': self.can_delete_activity_category(),
                'can_add_activity_tracking': self.can_add_activity_tracking(),
                'can_edit_activity_tracking': self.can_edit_activity_tracking(),
                'can_delete_activity_tracking': self.can_delete_activity_tracking()
            }
        }
