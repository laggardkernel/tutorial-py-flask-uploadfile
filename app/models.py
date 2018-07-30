#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import uuid
import os
from datetime import datetime
from werkzeug import secure_filename, cached_property
from flask import request
from app._compat import quote_plus
from app.ext import db, Model
from app.utils import get_file_md5, get_file_path
from app.mimes import IMAGE_MIMES, AUDIO_MIMES, VIDEO_MIMES
import cropresize2
from PIL import Image
import short_url


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
        # TODO: secure filename with db event listener
        self.filename = secure_filename(filename) if filename else self.filehash
        self.filemd5 = filemd5

    @staticmethod
    def __hash_filename(filename):
        '''Generate a random name for uploaded file'''
        _, _, extension = filename.rpartition('.')
        return '%s.%s' % (uuid.uuid4().hex, extension)

    @property
    def path(self):
        return get_file_path(self.filehash)

    @classmethod
    def create_by_uploaded_file(cls, uploaded_file):
        r = cls(uploaded_file.filename, uploaded_file.mimetype)
        uploaded_file.save(r.path)
        # skip saving current file if the same file exists (comparision by md5)
        with open(r.path, 'rb') as f:
            filemd5 = get_file_md5(f)
            uploaded_file = cls.query.filter_by(filemd5=filemd5).first()
            if uploaded_file:
                os.remove(r.path)
                return uploaded_file
        filestat = os.stat(r.path)
        r.size = filestat.st_size
        r.filemd5 = filemd5
        # commit db session in the outside view
        return r

    @classmethod
    def resize(cls, old_file, width, height):
        assert old_file.is_image, TypeError('Unsupported Image Type.')

        img = cropresize2.crop_resize(
            Image.open(old_file.path), (int(width), int(height))
        )
        r = cls(old_file.filename, old_file.mimetype)
        img.save(r.path)
        filestat = os.stat(r.path)
        r.size = filestat.st_size
        # commit db session in the outside view
        return r

    @property
    def url_i(self):
        return self.get_url('i')

    @property
    def url_p(self):
        '''Preview URL'''
        return self.get_url('p')

    @property
    def url_s(self):
        '''Short URL'''
        return self.get_url('s', is_short=True)

    @property
    def url_d(self):
        '''Download URL'''
        return self.get_url('d')

    @property
    def quoteurl(self):
        return quote_plus(self.url_i)

    # Helpers

    @property
    def is_image(self):
        return self.mimetype in IMAGE_MIMES

    @property
    def is_audio(self):
        return self.mimetype in AUDIO_MIMES

    @property
    def is_video(self):
        return self.mimetype in VIDEO_MIMES

    @property
    def is_pdf(self):
        return self.mimetype == 'application/pdf'

    @property
    def type(self):
        for t in ('image', 'audio', 'video', 'pdf'):
            if getattr(self, 'is_' + t):
                return t
        return 'binary'

    @cached_property
    def shortlink(self):
        '''Generate short link with id'''
        return short_url.encode_url(self.id)

    def get_url(self, subtype, is_short=False):
        hash_or_link = self.shortlink if is_short else self.filehash
        return 'http://{host}/{subtype}/{hash_or_link}'.format(
            subtype=subtype, host=request.host, hash_or_link=hash_or_link
        )
