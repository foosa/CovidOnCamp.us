# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys

from flask import Flask, render_template, redirect, url_for, request, current_app
import flask_admin as admin
from flask_admin import helpers, expose
from flask_admin.contrib import sqla, fileadmin
import flask_login as login
from sarscov2_gatech_community_survey import commands, public, user, api, manage
from sarscov2_gatech_community_survey.user.models import Role
from sarscov2_gatech_community_survey.extensions import (
    bcrypt,
    cache,
    csrf_protect,
    db,
    mail,
    debug_toolbar,
    flask_static_digest,
    login_manager,
    migrate,
)


class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not login.current_user.is_authenticated:
            return False
        if not login.current_user.is_admin:
            return False
        role = Role.query.filter_by(user_id=login.current_user.id).first()
        if role and role.name == "admin":
            return True
        return False

    def on_model_change(self, form, model, is_created=False):
        if hasattr(model, 'password'):
            if is_created:
                model.password = bcrypt.generate_password_hash(form.password.data)
            elif not login.current_user.check_password(form.password.data):
                model.password = bcrypt.generate_password_hash(form.password.data)
            if type(model.password) != bytes:
                model.password = bytes(model.password, 'utf-8')
        pass

# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    @login.login_required
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('public.home'))
        if not login.current_user.is_admin:
            return redirect(url_for('public.home'))
        else:
            role = Role.query.filter_by(user_id=login.current_user.id)
            if not role or role.name != "admin":
                return redirect(url_for('public.home'))
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    @login.login_required
    def logout_view(self):
        login.logout_user(login.current_user.id)
        flash("You are logged out.", "info")
        return redirect(url_for("public.home"))

def create_app(config_object="sarscov2_gatech_community_survey.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    admin_app = admin.Admin(app, index_view=MyAdminIndexView(), template_mode='bootstrap3', base_template='admin/index.html')
    admin_app.add_view(MyModelView(user.models.User, db.session))
    admin_app.add_view(MyModelView(user.models.Results, db.session))
    admin_app.add_view(MyModelView(user.models.Consent, db.session))
    admin_app.add_view(MyModelView(user.models.Role, db.session))
    admin_app.add_view(MyModelView(user.models.AuditLog, db.session))
    admin_app.add_view(MyModelView(user.models.UserInfo, db.session))
    admin_app.add_view(fileadmin.FileAdmin(app.config['UPLOAD_FOLDER'], name='Files'))
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    # bootstrap = Bootstrap(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    flask_static_digest.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(api.views.blueprint)
    app.register_blueprint(manage.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
