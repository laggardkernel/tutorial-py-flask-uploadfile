#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

from contextlib import contextmanager
from flask_mako import MakoTemplates, render_template  # noqa: F401
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery

mako = MakoTemplates()


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            # jump out and execute db statements, which is equivalent to
            # running db statements under current context
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        # query un-deleted (soft) data by default
        if "is_deleted" not in kwargs:
            kwargs["is_deleted"] = 0
        return super().filter_by(**kwargs)


db = SQLAlchemy(query_class=Query)


class Model(db.Model):  # noqa
    # Disable table creation
    __abstract__ = True
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def set_attrs(self, attrs_dict):
        '''Helper used to fill form data into model instance'''
        for key, value in attrs_dict.items():
            # in case the attr is write-only
            if hasattr(self.__class__, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.is_deleted = True
