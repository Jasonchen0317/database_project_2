from flask import Flask, render_template, request, url_for, redirect, session
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, HiddenField, TextAreaField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError

def isinteger(form, field):
    if not field.data.isdigit():
        raise ValidationError('invalid')

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    address = StringField('Address', validators=[])
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    profile = TextAreaField('Profile', validators=[])
    submit = SubmitField('Sign Up')


class EditForm(FlaskForm):
    address = StringField('Address', validators=[])
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    profile = TextAreaField('Profile', validators=[])
    submit = SubmitField('Update')

class ThreadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    target = SelectField('Target', choices=[])
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    body=TextAreaField('Post', validators=[])
    submit = SubmitField('Post')

class ReplyForm(FlaskForm):
    body = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Reply')

class BlockForm(FlaskForm):
    join = SelectField('Join or Follow', choices=[('true', 'Join'), ('false', 'Follow')], validators=[DataRequired()])
    blockid = SelectField('Block', choices=[], validators=[DataRequired()])
    submit = SubmitField('Send')

class SearchBar(FlaskForm):
    keyword = StringField('Keyword', validators=[DataRequired()])
    submit = SubmitField('Search')

class FriendRequestForm(FlaskForm):
    users = SelectField('Users', choices=[], validators=[DataRequired()])
    submit = SubmitField('Send')
