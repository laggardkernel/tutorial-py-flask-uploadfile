#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import os
from flask_migrate import Migrate
from app import create_app
from app.ext import db
from app.models import UploadedFile

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# Initialize Flask-Migrate, sub-command "db" is added automatically
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    '''
    Load models into shell by default
    '''
    return dict(app=app, db=db, UploadedFile=UploadedFile)


@app.cli.command()
def deploy():
    from flask_migrate import upgrade

    upgrade()
