#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import uuid
from datetime import datetime
from app.ext import db, Model


class UploadedFile(Model):
    __tablename__ = 'uploadedfiles'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    filename = db.Column(db.String(5000), nullable=False)
    filehash = db.Column(db.String(128), nullable=False, unique=True)
    filemd5 = db.Column(db.String(128), nullable=False, unique=True)
    uploaded_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mimetype = db.Column(db.String(256), nullable=False)
    size = db.Column(db.Integer, nullable=False, default=0)

    def __init__(
        self,
        filename='',
        mimetype='application/octet-stream',
        size=0,
        filehash=None,
        filemd5=None,
    ):
        self.uploaded_time = datetime.utcnow()
        self.mimetype = mimetype
        self.size = int(size)
        self.filehash = filehash if filehash else self.__hash_filename(filename)
        self.filename = filename if filename else self.filehash
        self.filemd5 = filemd5

    @staticmethod
    def __hash_filename(filename):
        _, _, extension = filename.rpartition('.')
        return '%s.%s' % (uuid.uuid4().hex, extension)
