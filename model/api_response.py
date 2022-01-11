from flask_login import current_user
import datetime

class APIResponse:

    is_successful = True
    error_message = ''
    data = {}

    def __init__(self, is_successful, error_message, data):
        self.is_successful = is_successful
        self.error_message = error_message
        self.data = data
    
    def serialize(self):
        return {
            'is_successful': self.is_successful,
            'error_message': self.error_message,
            'data': self.data
        }
