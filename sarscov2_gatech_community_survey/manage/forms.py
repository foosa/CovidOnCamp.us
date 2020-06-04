# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import phonenumbers
from sarscov2_gatech_community_survey.user.models import User


class barcodeForm(FlaskForm):
    """Barcode entry"""
    barcode = StringField(
        "Sample ID", validators=[DataRequired(), Length(min=18, max=21)]
    )

class detailsForm(FlaskForm):
    """Barcode entry"""
    barcode = StringField(
        "Sample ID", validators=[DataRequired(), Length(min=18, max=21)]
    )
    consent_id = StringField(
        "Consent ID", validators=[DataRequired()]
    )
    fname = StringField(
            "First name", validators=[DataRequired(), Length(min=3)]
    )
    lname = StringField(
            "Last name", validators=[DataRequired(), Length(min=3)]
    )
    gtid = StringField(
            "GTID", validators=[DataRequired(), Length(min=9, max=9)]
    )


