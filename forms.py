from flask import Flask, render_template, request, url_for, redirect, session
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, HiddenField, TextAreaField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    address = StringField('Address', validators=[])
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    profile = TextAreaField('Profile', validators=[])
    submit = SubmitField('Sign In')

class EditForm(FlaskForm):
    address = StringField('Address', validators=[])
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    profile = TextAreaField('Profile', validators=[])
    submit = SubmitField('Update')

class ThreadForm(FlaskForm):
    title = StringField('Title', validators=[])
    target = SelectField('Target', choices=[('friend', 'Friend'), ('neighbor', 'Neighbor'), ('hood', 'Hood'), ('block', 'Block')])
    rid=StringField('Recipient', validators=[])
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    body=TextAreaField('Body', validators=[])
    submit = SubmitField('Post')

class ReplyForm(FlaskForm):
    body = TextAreaField('Reply', validators=[])
    submit = SubmitField('Reply')
    