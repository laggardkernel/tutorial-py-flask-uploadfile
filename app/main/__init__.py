#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

from flask import Blueprint

main = Blueprint('main', __name__)

# Import views at the end in case of dependency loop
from . import views  # noqa: E402
