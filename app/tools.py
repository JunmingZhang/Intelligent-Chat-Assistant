from app import dynamodb, s3, log, webapp

import re
import os

# dynamodb = DynamoDBConn()
# s3 = S3Conn()

# log = logging.getLogger(__name__)


# ===== Tools START =====
def sign_up(email_addr, username, password, avatar_path):

    # validate email address
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not EMAIL_REGEX.match(email_addr):
        log.warning("Please give an email in correct format.")
        return {
            "success": False,
            "details": {
                "email": ["Please give an email in correct format."]
            }
        } 
    
    # validate password
    if len(password) <= 5:
        log.warning("Password has at least 6 characters.")
        return {
            "success": False,
            "details": {
                "password": ["Password has at least 6 characters."]
            }
        }

    # record user info in database
    response = dynamodb.userinfo_put_item(
        email_addr=email_addr,
        username=username,
        password=password)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        log.error("The email account has been used.")
        return {
            "success": False,
            "details": {
                "email": ["The email account has been used."]
            }
        } 
    
    # upload an avatar
    response = s3.upload_avatar(avatar_path, email_addr)

    # record info of user logs
    response = dynamodb.userlog_put_item(
        email_addr=email_addr,
        username=username
    )

    # assign an empty chatlog to the user
    response = s3.upload_chatlog(email_addr)
    log.info("signup for user {} with email address {} succeed!".format(username, email_addr))

    # create local user files
    userfile_path = webapp.config['UPLOAD_FOLDER']
    local_path = os.path.join(userfile_path, email_addr)
    if not os.path.exists(userfile_path):
        os.makedirs(userfile_path)
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    
    return {
        "success": True,
        "details": "Success."
    } 

def sign_in(email_addr, password):
    """
    get user info if given info is correct
    """
    userinfo = dynamodb.userinfo_query(email_addr, password)
    if len(userinfo) == 0:
        log.warning("either email address and password is incorrect.")
        return {
            "success": False,
            "details": {
                "email": ["Either email address and password is incorrect."],
                "password": ["Either email address and password is incorrect."]
            }
        }
    username = userinfo[0]['username']
    
    userlog = dynamodb.userlog_query(email_addr, username)
    dynamodb.update_userlog_last_action_time(email_addr, username)

    userfile_path = './app/static/userfiles'
    local_path = os.path.join(userfile_path, email_addr)
    
    local_avatar_path = os.path.join(local_path, 'avatar.png')
    s3.download_avatar(email_addr, local_avatar_path)

    local_chatlog_path = os.path.join(local_path, 'chatlog.txt')
    s3.download_avatar(email_addr, local_chatlog_path)

    return {
        "success": True,
        "details": {
            "user_info": userinfo,
            "user_log": userlog,
            "local_avatar_path": local_avatar_path,
            "local_chatlog_path": local_chatlog_path
        }
    } 

def get_chatlog(email_addr):
    userfile_path = './app/static/userfiles'
    local_path = os.path.join(userfile_path, email_addr, 'chatlog.txt')
    s3.download_chatlog(email_addr, local_path)

def update_chatlog(email_addr, username, text):
    dynamodb.update_userlog_last_action_time(email_addr, username)
    s3.upload_chatlog(email_addr, text)

# ===== Tools END =====

# API starts here

if __name__ == "__main__":
    dynamodb.create_signup_table()
    dynamodb.create_chatlog_table()
    s3.create_bucket()

    email_addr = 'andy@zhang.com'
    username = 'andy'
    password = '123456'
    avatar_path = './app/static/test_images/3.jpeg'
    sign_up(email_addr, username, password, avatar_path)
    userinfo, userlog, local_avatar_path, local_chatlog_path = sign_in(email_addr, username, password)
    print(userinfo)
    print(userlog)
    print(local_avatar_path)
    print(local_chatlog_path)

    update_chatlog(email_addr, username, "cool day!")
    get_chatlog(email_addr)
    dynamodb.clean_user(email_addr, username)
