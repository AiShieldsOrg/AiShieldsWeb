from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()],default='')
    passphrase = PasswordField('Password', validators=[DataRequired()],default='')
    submit = SubmitField('Sign In')
