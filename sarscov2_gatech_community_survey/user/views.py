# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, jsonify
from flask_login import login_required, current_user
from .forms import UpdateForm, UpdatePassword
from sarscov2_gatech_community_survey.user.models import User, Results, Consent
from sarscov2_gatech_community_survey.extensions import db
from sarscov2_gatech_community_survey.api.views import add_consent

blueprint = Blueprint("user_bp", __name__, url_prefix="/dashboard", static_folder="../static")



@blueprint.route("/")
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
                           fwd=False
                           )

@blueprint.route("/_get_results")
@login_required
def _get_results():
    """User dashboard."""
    results = Results.query.filter_by(user_id=current_user.id).all()
    return jsonify(data=render_template('users/results.html',
                    template='results-template',
                    results=results
                    )
                   )

@blueprint.route("/sign")
@login_required
def sign():
    """User dashboard."""
    fwd = "https://powerforms.docusign.net/d1ce1898-d9eb-4bcd-97cf-27be91d11036?env=na3-eu1&acct=7554587e-5afc-4247-8977-071ef5c80e3b&Participant_UserName"
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
                           fwd=fwd
                           )



@blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Update user settings."""
    info = UpdateForm()
    pwd = UpdatePassword()
    current_app.logger.error(info)
    if info.submit_info.data and info.validate_on_submit():
        user = current_user
        user.first_name = info.fname.data
        user.last_name = info.lname.data
        user.save()
        return redirect(url_for('user_bp.settings'))
    if pwd.submit_pwd.data and pwd.validate_on_submit():
        if not current_user.check_password(pwd.oldpwd.data):
            flash('Current password is incorrect', 'danger')
        user = current_user
        user.set_password(pwd.newpwd.data)
        user.save()  # Create new user
        return redirect(url_for('user_bp.settings'))
    return render_template('users/settings.jinja2',
                           title='Update account settings.',
                           info=info,
                           pwd_update=pwd,
                           template='settings-page',
                           body="Update user account.")



