# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from sarscov2_gatech_community_survey.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from sarscov2_gatech_community_survey.extensions import bcrypt
from sarscov2_gatech_community_survey.utils import get_random_alphaNumeric_string

def roundSeconds(dateTimeObject):
    newDateTime = dateTimeObject

    if newDateTime.microsecond >= 500000:
        newDateTime = newDateTime + dt.timedelta(seconds=1)

    return newDateTime.replace(microsecond=0)

class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = "roles"
    name = Column(db.String(80), unique=False, nullable=False)
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="roles")

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"

class Results(SurrogatePK, Model):
    """Test results"""

    __tablename__ = "results"
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="results")
    start_time = Column(db.DateTime, nullable=False, default=roundSeconds(dt.datetime.now()))
    updated_time = Column(db.DateTime, nullable=False, default=None)
    result_id = Column(db.String(200), nullable=True, default=None)
    result = Column(db.Boolean, nullable=True, default=None)
    result_text = Column(db.String(500), nullable=True, default="Sample pending")
    def __init__(self, user_id, result_id, **kwargs):
        """Create instance."""
        db.Model.__init__(self, user_id=user_id, result_id=result_id, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Result({self.result_id})>"

class Consent(SurrogatePK, Model):
    """Consent data"""

    __tablename__ = "consent"
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="consent")
    consented = Column(db.Boolean, nullable=True, default=None)
    consent_id = Column(db.String(200), nullable=True, default="No consent id available")
    unverified = Column(db.Boolean, default=False, nullable=False)

    def __init__(self, user_id, consented, consent_id, **kwargs):
        """Create instance."""
        db.Model.__init__(self, user_id=user_id, consented=consented, consent_id=consent_id, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<ConsentID({self.consent_id})>"


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = "users"
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    phone = Column(db.String(20), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.LargeBinary(128), nullable=True)
    api_key = db.Column(db.String(30), unique=True, default=None)
    recovery_key = db.Column(db.String(30), default=None, nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=roundSeconds(dt.datetime.utcnow()))
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)
    sample_id = db.Column(db.String(30), default=get_random_alphaNumeric_string(16), nullable=False)
    # role = reference_col("roles", nullable=True)
    # Role = relationship("Role", backref="users")
    # consent_id = reference_col("consent", nullable=True)
    # consent = relationship("Consent", backref="consent")


    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<User({self.username!r})>"
