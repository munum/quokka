#!/usr/bin/env python
# -*- coding: utf-8 -*

import logging

from flask import request, session
from flask.ext.admin import Admin
from flask.ext.admin.babel import gettext, ngettext, lazy_gettext

from .models import ModelAdmin, FileAdmin
from .views import IndexView

logger = logging.getLogger()


class QuokkaAdmin(Admin):
    def register(self, model, view=None, *args, **kwargs):
        View = view or ModelAdmin
        self.add_view(View(model, *args, **kwargs))
        # try:
        #     self.add_view(View(model, *args, **kwargs))
        # except Exception as e:
        #     logger.warning(
        #         "admin.register({0}, {1}, {2}, {3}) error: {4}".format(
        #             model, view, args, kwargs, e.message
        #         )
        #     )


def create_admin(app=None):
    return QuokkaAdmin(app, index_view=IndexView())


def configure_admin(app, admin):

    ADMIN = app.config.get(
        'ADMIN',
        {
            'name': 'Quokka Admin',
            'url': '/admin'
        }
    )

    for k, v in list(ADMIN.items()):
        setattr(admin, k, v)

    babel = app.extensions.get('babel')
    if babel:
        try:
            @babel.localeselector
            def get_locale():
                override = request.args.get('lang')

                if override:
                    session['lang'] = override

                return session.get('lang', 'en')
            admin.locale_selector(get_locale)
        except:
            pass  # Exception: Can not add locale_selector second time.

    for entry in app.config.get('FILE_ADMIN', []):
        try:
            admin.add_view(
                FileAdmin(
                    entry['path'],
                    entry['url'],
                    name=entry['name'],
                    category=entry['category'],
                    endpoint=entry['endpoint']
                )
            )
        except:
            pass  # TODO: check blueprint endpoisnt colision

    if admin.app is None:
        admin.init_app(app)

    return admin


def _(*args, **kwargs):
    return gettext(*args, **kwargs)


def _l(*args, **kwargs):
    return lazy_gettext(*args, **kwargs)


def _s(*args, **kwargs):
    return ngettext(*args, **kwargs)
