# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length
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



class userInfoForm(FlaskForm):
    """Barcode entry"""
    fname = StringField(
            "First name", validators=[DataRequired(), Length(min=3)]
    )
    lname = StringField(
            "Last name", validators=[DataRequired(), Length(min=3)]
    )
    gtid = StringField(
            "GTID", validators=[DataRequired(), Length(min=9, max=9)]
    )
    dob = DateField("DOB", validators=[DataRequired()])
    race = SelectField(
            "Race", validators=[DataRequired()],
            choices=[('American Indian or Alaska Native','American Indian or Alaska Native'),
                     ('Asian','Asian'),
                     ('Black or African American','Black or African American'),
                     ('Native Hawaiian or other Pacific Islander', 'Native Hawaiian or other Pacific Islander'),
                     ('White', 'White')]
    )
    ethnicity = SelectField(
            "Ethnicity", validators=[DataRequired()],
            choices=[('Hispanic or Latino','Hispanic or Latino'), ('Not Hispanic or Latino','Not Hispanic or Latino')]
    )
    address = StringField(
            "Address", validators=[DataRequired(), Length(min=5)]
    )
    zipcode = StringField(
            "Zipcode", validators=[DataRequired(), Length(min=5, max=5)]
    )
    county = StringField(
            "County", validators=[DataRequired(), Length(min=3)]
    )




