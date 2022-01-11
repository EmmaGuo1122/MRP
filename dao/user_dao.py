from model.user import User
from utils import prj_constants
from utils.db_utilities import db
from sqlalchemy import select

class UserDAO:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get_user_by_username(self, username):
        return User.query.filter_by(username = username).first()
    
    def get_user_by_email(self, email):
        return User.query.filter_by(email = email).first()

    def get_user_by_id(self, id):
        return User.query.get(int(id))
    
    def get_user_by_site(self, site_id):
        return User.query.filter_by(site_id = site_id).all()
    
    def get_user_by_role(self, role):
        return User.query.filter_by(role = role).all()
    
    def get_all_users(self):
        # rows = db.session.execute(select(User)).all()
        # if rows:
        #     users = [row._mapping['User'] for row in rows if row]
        #     return users
        
        # return []
        return User.query.filter(User.role != prj_constants.USER_ROLE_SUPER_ADMIN).all()

    def save_one_user(self, user):
        db.session.add(user)

    def delete_one_user(self, user):
        db.session.delete(user)