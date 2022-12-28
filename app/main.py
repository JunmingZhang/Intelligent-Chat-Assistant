from app import webapp, dynamodb, s3, log
from app.forms import ChatForm, LoginForm, SignupForm
from app.tools import sign_up, sign_in, get_chatlog, update_chatlog
from app.conversation import Conversation, GPTConversation

from flask import Flask, request, session, jsonify, render_template, redirect, url_for
from datetime import datetime, timezone
from typing import Optional, Dict

import requests
import json
import os
import datetime


def _delete_session_variable(variable: str) -> None:
    try:
        del session[variable]
    except KeyError:
        pass


def _download_latest_chatlog(user_log: Dict, local_chatlog_path: str) -> Optional[str]:
    get_chatlog(email_addr=user_log.get("email_addr"))
    try:
        with open(local_chatlog_path, 'r') as chatlog_file:
            chatlog = chatlog_file.read()
    except:
        chatlog = None
    
    return chatlog


@webapp.route('/login', methods=['POST', 'GET'])
def login():
    next_page = request.args.get('next', None)

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        result = sign_in(
            email_addr=email,
            password=password
        )

        if result.get("success") is False:
            email_error, pass_error = False, False

            if "email" in list(result.get("details").keys()):
                email_error = True
            
            if "password" in list(result.get("details").keys()):
                pass_error = True

            return render_template(
                '/pages/welcome.html',
                form=form,
                email_error=email_error,
                pass_error=pass_error
            )
        
        user_information = result["details"]
        
        session["user_info"] = user_information["user_info"]
        session["user_log"] = user_information["user_log"]
        session["local_avatar_path"] = user_information["local_avatar_path"]
        session["local_chatlog_path"] = user_information["local_chatlog_path"]
        
        if next_page is not None and next_page != "":
            return redirect(url_for(next_page))
        
        return redirect(url_for('main'))

    return render_template(
        '/pages/welcome.html',
        form=form
    )


@webapp.route('/logout')
def logout():
    if session.get("user_log", None) is None:
        return redirect(url_for('login'))
    
    user_log = session.get("user_log")
    update_chatlog(email_addr=user_log.get("email_addr"), username=user_log.get("username"), text="")

    delete_variables = [
        'user_info',
        'user_log',
        'local_avatar_path',
        'local_chatlog_path'
    ]
    for variable in delete_variables:
        _delete_session_variable(variable)
    
    return redirect(url_for('login'))


@webapp.route('/signup', methods=['POST'])
def signup():
    form_data = dict(request.form)
    file_data = dict(request.files)

    email = form_data.get('email', None)
    username = form_data.get('username', None)
    password = form_data.get('password', None)
    password_again = form_data.get('password_again', None)
    avatar = file_data.get('avatar', None)

    form = SignupForm()
    form.email.data = email
    form.username.data = username
    form.password.data = password
    form.password_again.data = password_again
    form.avatar.data = avatar

    if form.validate():
        if form.password.data != form.password_again.data:
            return webapp.response_class(
                response=json.dumps(
                    {
                        "success": "false",
                        "details": {
                            "password": ["password does not match"],
                            "password_again": ["password does not match"],
                        }
                    }
                ),
                status=400,
                mimetype='application/json'
            )

        os.makedirs(webapp.config['TEMP_FOLDER'], exist_ok=True)
        path = os.path.join(webapp.config['TEMP_FOLDER'], form.avatar.data.filename)
        form.avatar.data.save(path)

        result = sign_up(
            email_addr=form.email.data,
            username=form.username.data,
            password=form.password.data,
            avatar_path=path
        )

        webapp.logger.info(result)

        if result.get("success") is False:
            return webapp.response_class(
                response=json.dumps(
                    {
                        "success": "false",
                        "details": result.get("details")
                    }
                ),
                status=401,
                mimetype='application/json'
            )

    else:
        webapp.logger.info(form.errors)

        return webapp.response_class(
            response=json.dumps(
                {
                    "success": "false",
                    "details": form.errors
                }
            ),
            status=402,
            mimetype='application/json'
        )
        
    return webapp.response_class(
        response=json.dumps(
            {
                "success": "true",
                "details": "sign up success!"
            }
        ),
        status=200,
        mimetype='application/json'
    )


@webapp.route('/end_conversation', methods=['POST'])
def end_conversation():
    if session.get("user_log", None) is None:
        return webapp.response_class(
            response=json.dumps(
                {
                    "success": "false",
                    "details": "user not login"
                }
            ),
            status=400,
            mimetype='application/json'
        )
    
    user_log = session.get("user_log")
    update_chatlog(email_addr=user_log.get("email_addr"), username=user_log.get("username"), text="")

    return webapp.response_class(
        response=json.dumps(
            {
                "success": "true",
                "details": "user end conversation"
            }
        ),
        status=200,
        mimetype='application/json'
    )


@webapp.route('/', methods=['GET', 'POST'])
@webapp.route('/main', methods=['GET', 'POST'])
def main():

    user_info = session.get("user_info", None)
    user_log = session.get("user_log", None)
    local_avatar_path = session.get("local_avatar_path", None)
    local_chatlog_path = session.get("local_chatlog_path", None)

    if not all([user_info, user_log, local_avatar_path, local_chatlog_path]):
        return redirect(url_for('login', next='main'))

    chatlog = _download_latest_chatlog(user_log, local_chatlog_path)

    form = ChatForm()
    conversation = GPTConversation(user=user_log.get("username"), chatbot="AI", chat_log=chatlog)
    if form.validate_on_submit():
        message = form.message.data
        chatlog = conversation.append_user_message_to_chatlog(message)
        bot_message = conversation.get_answer()
        chatlog = conversation.append_bot_message_to_chatlog(bot_message)

        update_chatlog(email_addr=user_log.get("email_addr"), username=user_log.get("username"), text=chatlog)

    return render_template(
        '/pages/convo.html', 
        user=conversation.get_user(), 
        bot=conversation.get_chatbot(), 
        warning=conversation.WARNING, 
        end=conversation.END,
        notification=conversation.NOTI,
        conversation=conversation.get_conversation(),
        form=form,
        user_email=user_log.get("email_addr"),
        user_avatar_path=local_avatar_path.split("./app/")[1],
        login=True
    )
