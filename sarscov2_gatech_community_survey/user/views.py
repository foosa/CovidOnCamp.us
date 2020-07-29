# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, jsonify, make_response
from flask_login import login_required, current_user
from .forms import UpdateForm, UpdatePassword, addTubeForm
from sarscov2_gatech_community_survey.user.models import User, Results, Consent, Role
from sarscov2_gatech_community_survey.utils import flash_errors
from sarscov2_gatech_community_survey.api.views import roundSeconds
import datetime as dt
from sarscov2_gatech_community_survey.extensions import db
from sarscov2_gatech_community_survey.api.views import add_consent
from functools import wraps


blueprint = Blueprint("user_bp", __name__, url_prefix="/dashboard", static_folder="../static")

@blueprint.route("/", methods=['GET'])
@login_required
def dashboard():
    """User dashboard."""
    consent = Consent.query.filter_by(user_id=current_user.id).first()
    result_num = Results.query.filter_by(user_id=current_user.id).count() + 1
    resultId = f"{current_user.sample_id}_{result_num}"
    return render_template('users/dashboard.jinja2',
                           title='COV2 dashboard',
                           template='dashboard-template',
                           consent=consent,
                           resultId=resultId,
                           fwd=False,
                           calendly=current_app.config['CALENDLY_LINK']
                           )

@blueprint.route("/resultid")
@login_required
def resultid():
    """User dashboard."""
    result_num = Results.query.filter_by(user_id=current_user.id).count() + 1
    resultId = f"{current_user.sample_id}_{result_num}"
    return make_response(resultId, 200)


@blueprint.route("/_get_results")
@login_required
def _get_results():
    """User dashboard."""
    results = Results.query.filter_by(user_id=current_user.id).all()
    return jsonify(data=render_template('users/results.html',
                    template='results-template',
                    results=results,
                    qualtrics=current_app.config['QUALTRICS_LINK']
                    )
                   )

@blueprint.route("/sign")
@login_required
def sign():
    """User dashboard."""
    fwd = current_app.config['POWERFORM_LINK']
    fwd +=f"={current_user.first_name} {current_user.last_name}"
    fwd += f"&Participant_Email={current_user.email}"
    consent = Consent.query.filter_by(user_id=current_user.id).first()
    result_num = Results.query.filter_by(user_id=current_user.id).count() + 1
    resultId = f"{current_user.sample_id}_{result_num}"
    if consent:
        consent.unverified = True
        consent.save()
    else:
        Consent.create(user_id=current_user.id, consented=False, unverified=True, consent_id=None)
    consent = Consent.query.filter_by(user_id=current_user.id).first()
    return render_template('users/dashboard.jinja2',
                           title='COV2 dashboard',
                           template='dashboard-template',
                           consent=consent,
                           resultId=resultId,
                           fwd=fwd,
                           calendly=current_app.config['CALENDLY_LINK']
                           )



@blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Update user settings."""
    info = UpdateForm()
    pwd = UpdatePassword()
    if info.submit_info.data and info.validate_on_submit():
        user = current_user
        user.first_name = info.fname.data
        user.last_name = info.lname.data
        user.save()
        return redirect(url_for('user_bp.settings'))
    if pwd.submit_pwd.data and pwd.validate_on_submit():
        if not current_user.check_password(pwd.oldpwd.value):
            flash('Current password is incorrect', 'danger')
        current_user.set_password(pwd.newpwd.data)
        current_user.save()  # update password
        flash('Password updated', 'success')
        return redirect(url_for('user_bp.settings'))
    return render_template('users/settings.jinja2',
                           title='Update account settings.',
                           info=info,
                           pwd_update=pwd,
                           template='settings-page',
                           body="Update user account.")


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_tube():
    form = addTubeForm()
    if form.validate_on_submit():
        result_num = Results.query.filter_by(user_id=current_user.id).count() + 1
        resultId = f"{current_user.sample_id}_{result_num}"
        Results.create(user_id=current_user.id,result_id=resultId, tube_id=form.tubeid.data, updated_time=roundSeconds(dt.datetime.now()))
        return redirect(url_for('user_bp.dashboard'))
    else:
        flash_errors(form)
    return render_template('users/add_tube.html',
                           title="Associated Tube ID with account",
                           form=form)


