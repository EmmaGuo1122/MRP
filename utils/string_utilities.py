import secrets
import string
from datetime import datetime
import re

def generate_temporary_password(length):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))

    return password

def format_canada_postal_code(postal_code):
    ret_str = postal_code.replace(" ", "")
    ret_str = ret_str[:3] + " " + ret_str[3:]

    return ret_str

def match_regex(regex, _str):
    return re.search(regex, _str) != None

def validate_username(username):
    '''
        Validate a username following the below rules:
        Refer to https://mkyong.com/regular-expressions/how-to-validate-username-with-regular-expression/

        1. Username consists of alphanumeric characters (a-zA-Z0-9), lowercase, or uppercase.
        2. Username allowed of the dot (.), underscore (_), and hyphen (-).
        3. The dot (.), underscore (_), or hyphen (-) must not be the first or last character.
        4. The dot (.), underscore (_), or hyphen (-) does not appear consecutively, e.g., java..regex
        5. The number of characters must be between 5 to 20.
    '''
    if not username:
        return False
    
    validate_regex = '^[a-zA-Z0-9]([._-](?![._-])|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$'
    return re.search(validate_regex, username) != None


def validate_password(password):
    '''
        Validate a password following the below rules:
        Refer to https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
        
        1. At least one upper case English letter
        2. At least one lower case English letter
        3. At least one digit
        4. At least one special character (?=.*?[#?!@$%^&*-])
        5. Minimum eight in length
    '''
    if not password:
        return False
    
    validate_regex = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\/])[A-Za-z\d@$!%*?&\/]{8,}$'
    return re.search(validate_regex, password) != None

def validate_email(email):
    '''
        Validate an email address following the below rules:
        Refer to https://stackoverflow.com/questions/64242568/validate-email-with-regular-expression-where-the-number-of-extensions-in-the-dom
    '''
    if not email:
        return False
    
    validate_regex = '^([0-9a-zA-Z-\.]+)@[a-zA-Z]{1,15}(?:\.[a-zA-Z]{1,5}){0,2}\.[a-zA-Z]{2,3}$'
    return re.search(validate_regex, email) != None

def validate_canada_postal_code(postal_code):
    '''
        Validate a Canadian postal code following the below rules:
        Refer to https://stackoverflow.com/questions/15774555/efficient-regex-for-canadian-postal-code-function
    '''
    if not postal_code:
        return False
    
    validate_regex = '^[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d$'
    return re.search(validate_regex, postal_code) != None

def convert_int_to_yyyymmdd_str(_num):
    try:
        return datetime.strptime(str(_num), '%Y%m%d').strftime('%Y/%m/%d')
    except:
        return None

def convert_yyyymmdd_str_to_int(_str):
    try:
        return int(datetime.strptime(_str, '%Y/%m/%d').strftime('%Y%m%d'))
    except:
        return None

def convert_int_to_hh24miss_str(_num):
    try:
        return datetime.strptime(str(_num).zfill(6), '%H%M%S').strftime('%H:%M:%S')
    except:
        return None

def convert_hh24miss_str_to_int(_str):
    try:
        return int(datetime.strptime(_str, '%H:%M:%S').strftime('%H%M%S'))
    except:
        return None