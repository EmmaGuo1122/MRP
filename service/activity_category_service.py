from dao.activity_category_dao import ActivityCategoryDAO
from utils.db_utilities import db
from flask_login import current_user
import datetime

class ActivityCategoryService:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #if db.session.is_active:
        #    db.session.close()
        pass

    def get_all_activity_categories(self):
        with ActivityCategoryDAO() as dao:
            return dao.get_all_activity_categories()
    
    def get_activity_category_by_id(self, id):
        with ActivityCategoryDAO() as dao:
            return dao.get_activity_category_by_id(id)
        
    def get_activity_category_by_code(self, code):
        with ActivityCategoryDAO() as dao:
            return dao.get_activity_category_by_code(code)
    
    def save_one_activity_category(self, activity_category):
        with ActivityCategoryDAO() as dao:
            activity_category.updated_by = current_user.id
            activity_category.updated_on = datetime.datetime.now().isoformat()
            dao.save_one_activity_category(activity_category)
            db.session.commit()
    
    def delete_one_activity_category(self, activity_category_id):
        with ActivityCategoryDAO() as dao:
            activity_category = dao.get_activity_category_by_id(activity_category_id)
            dao.delete_one_activity_category(activity_category)
            db.session.commit()