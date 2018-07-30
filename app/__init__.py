#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

from flask import Flask
from werkzeug import SharedDataMiddleware
from config import config
from app.ext import db, mako
from app.utils import get_file_path


def create_app(config_name='default'):
    '''
    factory function creates and initialize app instance
    '''
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # init of plugins

    # blueprints
    db.init_app(app)
    mako.init_app(app)

    # TODO: ?
    # read source file by SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/i/': get_file_path()})

    return app
