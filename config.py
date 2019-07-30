#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import os

basedir = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to gue55 sting"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Relative to project root folder
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(
        basedir, 'tmp/permdir'
    )

    @classmethod
    def init_app(cls, app):
        if not os.path.exists(cls.UPLOAD_FOLDER):
            os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL'
    ) or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite3')

    @classmethod
    def init_app(cls, app):
        from flask_debugtoolbar import DebugToolbarExtension

        toolbar = DebugToolbarExtension(app)  # noqa: F841


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL'
    ) or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite3')
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        from flask_debugtoolbar import DebugToolbarExtension

        toolbar = DebugToolbarExtension(app)  # noqa: F841


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL'
    ) or 'sqlite:///' + os.path.join(basedir, 'data.sqlite3')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # TODO: rotating logging


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
