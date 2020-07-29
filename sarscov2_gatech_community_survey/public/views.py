# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    send_file
)
from flask_login import login_required, login_user, logout_user, current_user

from sarscov2_gatech_community_survey.extensions import login_manager
from sarscov2_gatech_community_survey.public.forms import LoginForm, ForgotForm, ResetForm
from sarscov2_gatech_community_survey.user.forms import RegisterForm
from sarscov2_gatech_community_survey.user.models import User, Results
from sarscov2_gatech_community_survey.utils import flash_errors, get_random_alphaNumeric_string
from sarscov2_gatech_community_survey.api.views import send_welcome, reset_pwd
from sarscov2_gatech_community_survey.api.views import roundSeconds
import datetime as dt
blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('public.home'))

@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.headers.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None



@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    total = Results.query.filter(Results.result.isnot(None)).count()
    if total == 0: total = 1
    positive = Results.query.filter_by(result=True).count()
    negative = Results.query.filter_by(result=False).count()
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user, remember=True)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("user_bp.dashboard")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form, total=total, positive=positive, negative=negative)

@blueprint.route("/stats", methods=["GET", "POST"])
def dashboard():
    """Home page."""
    return send_file("templates/public/dashboard.html")


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user_bp."""
    if current_user and current_user.is_authenticated:
        return redirect(url_for("user_bp.dashboard"))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        import random
        import string
        lettersAndDigits = string.ascii_letters + string.digits
        rand = random.SystemRandom()
        User.create(
            username=form.email.data,
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
            active=True,
            first_name=form.fname.data,
            last_name=form.lname.data,
            gtid=form.gtid.data,
            sample_id=''.join((rand.choice(lettersAndDigits) for i in range(16)))
        )
        flash("Thank you for registering.", "success")
        send_welcome(form.email.data, form.fname.data, form.lname.data)
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user)
        result_num = Results.query.filter_by(user_id=user.id).count() + 1
        resultId = f"{user.sample_id}_{result_num}"
        Results.create(user_id=user.id, result_id=resultId, tube_id=form.tubeid.data,
                       updated_time=roundSeconds(dt.datetime.now()))
        return redirect(url_for('user_bp.dashboard'))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)

@blueprint.route("/forgot/", methods=["GET", "POST"])
def forgot():
    """Register new user_bp."""
    user = ''
    if current_user and current_user.is_authenticated:
        user = current_user.username
    form = ForgotForm(request.form)
    if form.validate_on_submit():
        if form.email.data:
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                user.update(recovery_key=get_random_alphaNumeric_string())
                reset_pwd(user.email, user.username, user.recovery_key)
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/forgot.html", forgot=form, un = user)

@blueprint.route("/reset/", methods=["GET", "POST"])
def reset():
    """Register new user_bp."""
    import random
    import string

    form = ResetForm(request.form)
    code = request.args.get("code")
    if form.validate_on_submit():
        if form.code.data:
            user = User.query.filter_by(recovery_key=form.code.data).first()
            if user:
                user.update(recovery_key="")
                user.set_password(form.password.data)
                user.save()
                login_user(user)
        return redirect(url_for("user_bp.dashboard"))
    else:
        flash_errors(form)
    return render_template("public/reset.html", reset=form, code=code)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
