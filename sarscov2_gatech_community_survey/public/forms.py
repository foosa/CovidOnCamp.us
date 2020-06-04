# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask import Markup
from sarscov2_gatech_community_survey.user.models import User


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user:
            self.email.errors.append("Unknown email")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password, <a href="/forgot">try resetting your password</a>?')
            return False

        if not self.user.active:
            self.username.errors.append("User not activated")
            return False
        return True


class ForgotForm(FlaskForm):
    """Pass reset form"""

    email = StringField(
        "Email", validators=[Optional(), Email(), Length(min=6, max=40)]
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(ForgotForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(ForgotForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if self.email.data != "":
            return True
        else:
            return False

class ResetForm(FlaskForm):
    """Register form."""

    code = StringField(
        "Code", validators=[DataRequired(), Length(min=8, max=8)]
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
        super(ResetForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(ResetForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(recovery_key=self.code.data).first()
        if user:
            return True
        self.code.errors.append("Invalid reset code")
        return False

