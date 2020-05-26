# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import phonenumbers
from .models import User


class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=25)]
    )
    fname = StringField(
        "First name", validators=[DataRequired(), Length(min=3, max=25)]
    )
    lname = StringField(
        "Last name", validators=[DataRequired(), Length(min=3, max=25)]
    )
    phone = StringField(
        "Phone number", validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(min=6, max=40)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        "Verify password",
        [DataRequired(), EqualTo("password", message="Passwords must match")],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        try:
            p = phonenumbers.parse(self.phone.data)
            if not phonenumbers.is_valid_number(p):
                self.phone.errors.append("Not a valid phone number")
                return False
            user = User.query.filter_by(phone=self.phone.data).first()
            if user:
                self.phone.errors.append('Phone number already registered, <a href="/forgot">try resetting your password</a>?')
                return False
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            self.phone.errors.append("Not a valid phone number")
            return False
        return True

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class InfoForm(FlaskForm):
    """info form."""
    fname = StringField('First name',
                       validators=[DataRequired()])
    lname = StringField('Last name',
                       validators=[DataRequired()])
    phone = StringField('Phone number',
                        validators=[DataRequired()])
    email = StringField('Email',
                        validators=[])

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


class UpdateForm(InfoForm):
    submit_info = SubmitField('Update info')

class UpdatePassword(UpdateForm):
    """Update user info form."""
    oldpwd = PasswordField('Current Password',
                                 validators=[DataRequired(),
                                             Length(min=6, message='Seems to short to be a valid password')])
    newpwd = PasswordField('New Password',
                             validators=[DataRequired(),
                                         Length(min=6, message='Select a stronger password.')])
    confirm = PasswordField('Confirm Your New Password',
                            validators=[DataRequired(),
                                        EqualTo('newpwd', message='Passwords must match.')])
    submit_pwd = SubmitField('Update password')
