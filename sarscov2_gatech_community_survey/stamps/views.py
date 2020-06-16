# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, url_for, request, render_template, redirect, current_app, make_response, abort, Markup, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sarscov2_gatech_community_survey.utils import flash
from sarscov2_gatech_community_survey.user.models import Role, Results, UserInfo, User
from sarscov2_gatech_community_survey.extensions import db
import os
from sqlalchemy.ext.serializer import loads, dumps

blueprint = Blueprint("stamps", __name__, url_prefix="/stamps/", static_folder="../static")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['txt', 'tsv', 'csv']

@blueprint.route('/', methods=['GET'])
@login_required
def home():
    """Home page."""
    roles = Role.query.filter_by(user_id=current_user.id).all()
    if not roles or all([role.name != "stamps" for role in roles]):
        flash("You don't have permission to view this page")
        abort(404)
    # to_report = Results.query.filter_by(reported=False).join(User).join(UserInfo).all()
    to_report = db.session.query(Results, User, UserInfo)
    # to_report = to_report.filter(Results.reported == False).filter(Results.user_id == User.id).all()
    to_report = to_report.filter(Results.user_id == User.id).filter(Results.user_id == UserInfo.user_id).all()
    results = []
    columns = [
            {
                    "field" : "Result ID",
                    "title" : "Result ID",
                    "sortable" : True,
            },
            {
                    "field" : "First name",
                    "title" : "First name",
                    "sortable" : True,
            },
            {
                    "field" : "Last name",
                    "title" : "Last name",
                    "sortable" : True,
            },
            {
                    "field" : "Phone",
                    "title" : "Phone",
                    "sortable" : False,
            },
            {
                    "field" : "GTID",
                    "title" : "GTID",
                    "sortable" : True,
            },
            {
                    "field" : "Result",
                    "title" : "Result",
                    "sortable" : True,
            },
            {
                    "field" : "Patient age",
                    "title" : "Patient age",
                    "sortable" : True,
            },
            {
                    "field" : "Patient race",
                    "title" : "Patient race",
                    "sortable" : True,
            },
            {
                    "field" : "Patient ethnicity",
                    "title" : "Patient ethnicity",
                    "sortable" : True,
            },
            {
                    "field" : "Patient address",
                    "title" : "Patient address",
                    "sortable" : True,
            },
            {
                    "field" : "Patient zip",
                    "title" : "Patient zip",
                    "sortable" : True,
            },
            {
                    "field" : "Patient county",
                    "title" : "Patient county",
                    "sortable" : True,
            },


    ]
    for report in to_report:
        results.append( {
                "Result ID": report.Results.result_id,
                "First name": report.User.first_name,
                "Last name": report.User.last_name,
                "Phone": report.User.phone,
                "GTID": report.User.gtid,
                "result": str(report.Results.result),
                "Patient age": report.UserInfo.age,
                "Patient race": report.UserInfo.race,
                "Patient ethnicity": report.UserInfo.ethnicity,
                "Patient address": report.UserInfo.address,
                "Patient zip": report.UserInfo.zipcode,
                "Patient county": report.UserInfo.county,
        })
    return render_template('stamps/home.html',
                           data=results,
                           columns=columns)


