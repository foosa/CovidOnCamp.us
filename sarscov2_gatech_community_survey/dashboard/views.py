# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, url_for, request, render_template, redirect, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sarscov2_gatech_community_survey.utils import flash
from ..api.views import add_consent
import os
from sarscov2_gatech_community_survey.manage.forms import barcodeForm, detailsForm, userInfoForm
from sarscov2_gatech_community_survey.user.models import User, Results, Consent, dt, roundSeconds, AuditLog, UserInfo
from sarscov2_gatech_community_survey.utils import flash_errors
import plotly
import plotly.plotly as py
import plotly.graph_objs as pgo

blueprint = Blueprint("datadash", __name__, url_prefix="/data/", static_folder="../static")




@blueprint.route('/', methods=['GET'])
@login_required
def home():
    """Home page."""

    if current_user.is_admin:
        return render_template("manage/home.html",
                               consent=os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], 'consent')),
                               results=os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], 'results')))

