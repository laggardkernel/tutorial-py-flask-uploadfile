#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

import os
import hashlib
from functools import partial
from config import Config


def get_file_md5(f, chunk_size=1024 * 8):
    r = hashlib.md5()
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        else:
            r.update(chunk)
    return r.hexdigest()


def humanize_bytes(bytesize, precision=2):
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes'),
    )
    if bytesize == 1:
        return '1 byte'
    for factor, unit in abbrevs:
        if bytesize >= factor:
            break
    return '%.*f %s' % (precision, bytesize / factor, unit)


get_file_path = partial(os.path.join, Config.UPLOAD_FOLDER)
