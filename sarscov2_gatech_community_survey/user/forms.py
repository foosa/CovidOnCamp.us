# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
import phonenumbers
from .models import User, Results


class RegisterForm(FlaskForm):
    """Register form."""

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
    gtid = StringField(
        "GTID", validators=[DataRequired(), Length(min=9, max=9)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        "Verify password",
        [DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    tubeid = StringField(
        "Tube ID", validators=[Optional(), Length(min=6, max=40)]
    )
    tubeid_confirm = StringField(
        "Confirm Tube ID",
        [EqualTo("tubeid", message="Tube ID's must match")],
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
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        user = User.query.filter_by(email=self.gtid.data).first()
        if user:
            self.gtid.errors.append("GTID already registered")
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
        result = Results.query.filter_by(tube_id=self.tubeid.data).first()
        if self.tubeid.data and result:
            self.tubeid.errors.append("Tube ID has already been registered")
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

class addTubeForm(FlaskForm):
    """Associated TubeID with user from dashboard"""
    tubeid = StringField("Tube ID", validators=[DataRequired(), Length(min=8, max=8, message="Tube IDs are 8 characters long")])
    tubeid_confirm = StringField("Confirm Tube ID", validators=[DataRequired(), EqualTo("tubeid", message="Tube IDs must match")])

    def validate(self):
        """Validate the form."""
        initial_validation = super(addTubeForm, self).validate()
        if not initial_validation:
            return False
        result = Results.query.filter_by(tube_id=self.tubeid.data).first()
        if self.tubeid.data and result:
            self.tubeid.errors.append("Tube ID has already been registered")
            return False
        return True
