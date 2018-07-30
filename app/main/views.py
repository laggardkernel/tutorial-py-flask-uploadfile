#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

from flask import request, abort, jsonify
from . import main
from app.ext import db, render_template
from app.models import UploadedFile
from app.utils import humanize_bytes


@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        w = request.form.get('w')
        h = request.form.get('h')
        if not uploaded_file:
            return abort(400)  # Bad Request

        with db.auto_commit():
            # TODO: unique constraint failed
            if w and h:
                uploaded_file = UploadedFile.resize(uploaded_file, w, h)
            else:
                uploaded_file = UploadedFile.create_by_uploaded_file(uploaded_file)
            db.session.add(uploaded_file)

        return jsonify(
            {
                'url_d': uploaded_file.url_d,
                'url_i': uploaded_file.url_i,
                'url_s': uploaded_file.url_s,
                'url_p': uploaded_file.url_p,
                'filename': uploaded_file.filename,
                'size': humanize_bytes(uploaded_file.size),
                'time': str(uploaded_file.uploaded_time),
                'type': uploaded_file.type,
                'quoteurl': uploaded_file.quoteurl,
            }
        )

    return render_template('index.html', **locals())
