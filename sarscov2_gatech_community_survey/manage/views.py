# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, url_for, request, render_template, redirect, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sarscov2_gatech_community_survey.utils import flash
from ..api.views import add_consent
import os

blueprint = Blueprint("manage", __name__, url_prefix="/manage/", static_folder="../static")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['txt', 'tsv', 'csv']

@blueprint.route('/', methods=['GET'])
@login_required
def home():
    """Home page."""

    if current_user.is_admin:
        return render_template("manage/home.html",
                               consent=os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], 'consent')),
                               results=os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], 'results')))

@blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Home page."""
    if current_user.is_admin:
        if request.method == 'POST':
            if 'kind' not in request.form:
                flash('No upload type chosen')
                return redirect(request.url)
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],request.form['kind'], filename))
                return redirect(url_for('manage.home'))
        current_app.logger.info(os.listdir(current_app.config['UPLOAD_FOLDER']))
        return render_template("manage/home.html",
                               files=os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], 'consent')))

@blueprint.route('/update_consents', methods=['POST'])
@login_required
def update_consents():
    """Home page."""
    if current_user.is_admin:
        if request.method == 'POST':
            if 'consentfile' not in request.form or not allowed_file(request.form.get('consentfile')):
                flash('Selected file not in list of allowed files')
                return redirect(url_for('manage.home'))
            else :
                flash(f"Updating consent data with: {request.form.get('consentfile')}")
                fname = os.path.join(current_app.config['UPLOAD_FOLDER'], "consent", request.form.get('consentfile'))
                with open(fname, encoding='utf8') as fh:
                    fh.readline()
                    for l in fh:
                        l = l.rstrip().split(",")
                        add_consent(l[0],l[4])
                return redirect(url_for('manage.home'))
        current_app.logger.info(os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], 'results')))
        return redirect(url_for('manage.home'))

@blueprint.route('/update_results', methods=['GET'])
@login_required
def update_results():
    """Home page."""
    if current_user.is_admin:
        if request.method == 'POST':
            if 'resultsfile' not in request.form or not allowed_file(request.form.get('resultsfile')):
                flash('Selected file not in list of allowed files')
                return redirect(url_for('manage.home'))
            else:
                flash(f"Updating consent data with: {request.form.get('resultsfile')}")
                return redirect(url_for('manage.home'))
        current_app.logger.info(os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'],'results')))
        return redirect(url_for('manage.home'))

