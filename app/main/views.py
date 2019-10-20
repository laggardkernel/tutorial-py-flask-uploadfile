#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

from flask import request, abort, jsonify, current_app, send_from_directory, redirect
from . import main
from app.ext import db, render_template
from app.models import UploadedFile
from app.utils import humanize_bytes

ONE_MONTH = 60 * 60 * 24 * 30


@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        w = request.form.get('w')
        h = request.form.get('h')
        if not uploaded_file:
            return abort(400)  # Bad Request

        # TODO: unique constraint failed
        if w and h:
            uploaded_file = UploadedFile.resize(uploaded_file, w, h)
        else:
            uploaded_file = UploadedFile.create_by_uploaded_file(uploaded_file)
        uploaded_file.save()

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


@main.route('/r/<img_hash>')
def resize(img_hash):
    w = request.args.get('w')
    h = request.args.get('h')

    if w and h:
        old_file = UploadedFile.objects.get_or_404(filehash=img_hash)
        new_file = UploadedFile.resize(old_file, w, h)
        return new_file.url_i


@main.route('/d/<filehash>')
def download(filehash):
    # Note: the filehash contains file extension
    uploaded_file = UploadedFile.objects.get_or_404(filehash=filehash)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename=uploaded_file.filehash,
        cache_timeout=ONE_MONTH,
        as_attachment=True,
        attachment_filename=uploaded_file.filename,
    )


@main.route('/p/<filehash>')
def preview(filehash):
    uploaded_file = UploadedFile.objects.get_or_404(filehash=filehash)
    return render_template('success.html', p=uploaded_file)


@main.route('/s/<shortlink>')
def s(shortlink):
    uploaded_file = UploadedFile.get_file_by_shortlink(shortlink)
    return redirect(uploaded_file.url_p)
