from flask_login import current_user
from dao.user_dao import UserDAO
from model.user import User
from utils.db_utilities import db
import datetime

class UserService:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #if db.session.is_active:
        #    db.session.close()
        pass

    def get_user_by_username(self, username):
        with UserDAO() as dao:
            return dao.get_user_by_username(username)
    
    def get_user_by_email(self, email):
        with UserDAO() as dao:
            return dao.get_user_by_email(email)
    
    def get_user_by_id(self, id):
        with UserDAO() as dao:
            return dao.get_user_by_id(id)
    
    def get_all_users(self):
        with UserDAO() as dao:
            return dao.get_all_users()
    
    def get_users_by_site(self, site_id):
        with UserDAO() as dao:
            return dao.get_user_by_site(site_id)
    
    def get_users_by_role(self, role):
        with UserDAO() as dao:
            return dao.get_user_by_role(role)
    
    def save_one_user(self, user):
        with UserDAO() as dao:
            user.updated_by = current_user.id
            user.updated_on = datetime.datetime.now().isoformat()
            dao.save_one_user(user)
            db.session.commit()
    
    def delete_user(self, user_id):
        if user_id == current_user.id:
            return {'is_successfull': False, 'error_message': 'You cannot delete your user instance!'}
        
        if not current_user.can_delete_user():
            return {'is_successfull': False, 'error_message': 'You do not have permission to delete user!'}
        
        with UserDAO() as dao:
            u = dao.get_user_by_id(user_id)
            dao.delete_one_user(u)
            db.session.commit()

            return {'is_successfull': True, 'error_message': ''}