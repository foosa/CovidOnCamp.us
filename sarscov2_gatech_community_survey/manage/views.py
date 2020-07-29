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
        return redirect(url_for('manage.home'))


@blueprint.route('/sample', methods=['GET', 'POST'])
@login_required
def sample():
    """Track a new samples"""
    form = barcodeForm(request.form)
    if form.validate_on_submit():
        result = Results.query.filter_by(result_id=form.barcode.data).first()
        if result:
            return redirect(url_for('manage.details', barcode=form.barcode.data))
    if current_user.is_admin:
        return render_template("manage/sample.html",
                               form=form)

@blueprint.route('/details', methods=['GET', 'POST'])
@login_required
def details():
    """List participant details"""
    form = detailsForm(request.form)
    barcode = request.args.get('barcode')
    user = User.query.filter_by(sample_id=barcode.split("_")[0]).first()
    consent_id = ''
    consent = Consent.query.filter_by(user_id=user.id).first()
    result = Results.query.filter_by(result_id=barcode).first()
    if consent and consent.consent_id != "No consent id available":
        consent_id = consent.consent_id
    if current_user.is_admin:
        if form.validate_on_submit():
            result.tube_id = form.tubeid.data
            result.save()
            if form.consent_id.data != consent_id:
                if consent:
                    if consent.consent_id == "No consent id available" or consent.consent_id == None:
                        consent.consent_id = form.consent_id.data
                        consent.save()
                    else:
                        flash('You cannot replace an existing consent ID', 'danger')
                        return redirect(url_for('manage.details', barcode=barcode))
                else:
                    Consent.create(
                            user_id=user.id,
                            consented=True,
                            consent_id=form.consent_id.data,
                            unverified=False
                    )
            return redirect(url_for('manage.user_info', barcode=barcode))
        return render_template("manage/details.html",
                               form=form,
                               barcode=barcode,
                               consent_id=consent_id,
                               tubeid=result.tube_id,
                               user=user)

@blueprint.route('/user_info', methods=['GET', 'POST'])
@login_required
def user_info():
    """List participant details"""

    barcode = request.args.get('barcode')
    user = User.query.filter_by(sample_id=barcode.split("_")[0]).first()
    info = UserInfo.query.filter_by(user_id=user.id).first()
    if not info:
        UserInfo.create(user_id=user.id)
        info = UserInfo.query.filter_by(user_id=user.id).first()
        form = userInfoForm(request.form)
    else:
        form = userInfoForm(request.form)
        # form.sex = info.sex
        # form.race = info.race
        # form.ethnicity = info.ethnicity
        # form.process()
    if current_user.is_admin:
        if form.validate_on_submit():
            if user.gtid != form.gtid.data:
                user.gtid = form.gtid.data
                user.save()
            today = dt.date.today()
            dob = form.dob.data
            info.update(
                    commit=True,
                    age=today.year-dob.year,
                    # sex=form.sex.data,
                    dob=dob
                    # race=form.race.data,
                    # ethnicity=form.ethnicity.data,
                    # address=form.address.data,
                    # zipcode=form.zipcode.data,
                    # county=form.county.data
                    )
            result = Results.query.filter_by(result_id=barcode).first()
            result.result_text = "Sample received, awaiting processing"
            result.result = None
            result.updated_time = roundSeconds(dt.datetime.now())
            result.save()
            AuditLog.create(
                    user_id=user.id,
                    result_id=result.id,
                    status=f"Specimen received, in tube {result.tube_id}"
            )
            flash('Added sample for processing', 'success')
            return redirect(url_for('manage.sample'))
        else:
            flash_errors(form)
        return render_template("manage/user_info.html",
                               form=form,
                               barcode=barcode,
                               user=user,
                               info=info)


# @blueprint.route('/generate', methods=['GET', 'POST'])
# @login_required
# def user_info():
#     """Generate barcodes"""
#     if current_user.is_admin:
#         form = generateForm()
#         if form.validate_on_submit():
