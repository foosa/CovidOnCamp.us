# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env

env = Env()
env.read_env()
ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SESSION_COOKIE_SAMESITE = "Strict"
if not DEBUG:
	SESSION_COOKIE_SECURE = True
	REMEMBER_COOKIE_SECURE = True
SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SECRET_KEY = env.str("SECRET_KEY")
SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT")
BCRYPT_LOG_ROUNDS = env.int("BCRYPT_LOG_ROUNDS", default=13)
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_SERVER=env.str("MAIL_SERVER")
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=env.str("MAIL_USERNAME")
MAIL_PASSWORD=env.str("MAIL_PASSWORD")
MAIL_ASCII_ATTACHMENTS=True
UPLOAD_FOLDER=env.str("UPLOAD_FOLDER")
CALENDLY_LINK=env.str("CALENDLY_LINK")
POWERFORM_LINK=env.str("POWERFORM_LINK")
QUALTRICS_LINK=env.str("QUALTRICS_LINK")
