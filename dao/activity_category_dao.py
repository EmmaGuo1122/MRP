from model.activity_category import ActivityCategory
from utils.db_utilities import db

class ActivityCategoryDAO:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get_activity_category_by_id(self, id):
        return ActivityCategory.query.get(int(id))
    
    def get_activity_category_by_code(self, code):
        return ActivityCategory.query.filter_by(code = code).first()
    
    def get_all_activity_categories(self):
        return ActivityCategory.query.order_by(ActivityCategory.code.asc()).all()

    def save_one_activity_category(self, activity_category):
        db.session.add(activity_category)
    
    def delete_one_activity_category(self, activity_category):
        db.session.delete(activity_category)