from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


class ConnectForm(FlaskForm):
    name = StringField('Enter a name')
    message = StringField('Enter a message:', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Submit')

USER_CHOICES = [('developer', 'Developer'), ('admin', 'Admin')]

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[Email(message='Not a valid email address.'), DataRequired()])
    pet_name = SelectField('Role', validators=[DataRequired()], choices=USER_CHOICES, default='developer')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField('Confirm password', validators=[DataRequired()])
    profile_pic = FileField("Profile Picture")
    submit = SubmitField('Submit')

class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField('Submit')

TOPIC_CHOICES = [('Linux', 'Linux'), ('Docker', 'Docker'), ('Jenkins', 'Jenkins'), ('Git', 'Git'),
                     ('Kubernetes', 'Kubernetes'), ('Python', 'Python'), ('Raspberry-pi', 'Raspberry-pi'), ('Arduino', 'Arduino')]
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    #content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    #author = StringField('Author')
    #slug = StringField('Slug', validators=[DataRequired()])
    slug = SelectField('Topic', validators=[DataRequired()], choices=TOPIC_CHOICES)
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    searched = StringField('Searched')
    submit = SubmitField('Submit')
