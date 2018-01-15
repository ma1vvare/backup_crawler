#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':

    from flask import Flask
    from core.flaskweb.ui.view import ui

    portal = Flask(__name__, template_folder='core/flaskweb/templates', static_folder='core/flaskweb/static')
    
    portal.config.from_object('core.config')

    portal.register_blueprint(ui)

    # portal.run(host='10.3.60.202', port=8888, )
    portal.run(host='127.0.0.1', port=8887, )
