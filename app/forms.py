from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email


class ChatForm(FlaskForm):
    message = StringField('Write a message...', validators=[DataRequired()])
    submit = SubmitField('Send Message')


class LoginForm(FlaskForm):
    email = EmailField('Email address', [DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    email = EmailField('Email address', [DataRequired(), Email()])
    username = StringField('User name', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    password_again = StringField('Password again', validators=[DataRequired()])
    avatar = FileField('avatar', validators=[
        FileRequired(), 
        FileAllowed(['jpeg', 'jpg', 'png'], 'Images only!')
    ])
