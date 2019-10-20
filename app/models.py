#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import uuid
import os
from datetime import datetime
from werkzeug import secure_filename, cached_property
from flask import request, abort
from app._compat import quote_plus
from app.utils import get_file_md5, get_file_path
from app.mimes import IMAGE_MIMES, AUDIO_MIMES, VIDEO_MIMES
import cropresize2
from PIL import Image
import short_url

from mongoengine import (
    Document as BaseDocument,
    connect,
    ValidationError,
    DoesNotExist,
    QuerySet,
    MultipleObjectsReturned,
    IntField,
    DateTimeField,
    StringField,
    SequenceField,
)

connect(
    'r',
    host='localhost',
    port=27017,
    username='root',
    password='password',
    authentication_source='admin',
)


class BaseQuerySet(QuerySet):
    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except (MultipleObjectsReturned, DoesNotExist, ValidationError):
            abort(404)


class Document(BaseDocument):
    meta = {'abstract': True, "queryset_class": BaseQuerySet}


class UploadedFile(Document):
    meta = {'collection': 'uploadedfiles'}
    id = SequenceField(primary_key=True)
    # filename: original name and name used to display in the web page
    filename = StringField(max_length=5000, null=False)
    # filehash: random name used in storage
    filehash = StringField(max_length=128, null=False, unique=True)
    filemd5 = StringField(max_length=128, null=False, unique=True)
    uploaded_time = DateTimeField(null=False)
    mimetype = StringField(max_length=256, null=False)
    size = IntField(null=False)

    def __init__(
        self,
        filename='',
        mimetype='application/octet-stream',
        size=0,
        filehash=None,
        filemd5=None,
        *args,
        **kwargs,
    ):
        super().__init__(
            filename=filename,
            mimetype=mimetype,
            size=size,
            filehash=filehash,
            filemd5=filemd5,
            *args,
            **kwargs,
        )
        self.uploaded_time = datetime.utcnow()
        # the mimetype is provided in the uploaded file by the browser
        self.mimetype = mimetype
        self.size = int(size)
        # random name used in storage
        self.filehash = filehash if filehash else self.__hash_filename(filename)
        # TODO: secure filename with db event listener
        self.filename = secure_filename(filename) if filename else self.filehash
        # the real identifier for the file
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
            uploaded_file = cls.objects(filemd5=filemd5)
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
        """
        Resize the image and return a new image (the old one is kept)
        """
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

    @classmethod
    def get_file_by_shortlink(cls, shortlink, code=404):
        id = short_url.decode_url(shortlink)
        return cls.objects.get_or_404(id=id)

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
