#!/usr/bin/env python3
# License: GPL-3.0

from flask import Blueprint, render_template

################################################################################
#
# This file holds the Blueprint for setting up routes to error pages
#
################################################################################
class Error(object):

    def __init__(self, app):
        app.register_blueprint(self.ErrorRoutes)


    ErrorRoutes = Blueprint('ErrorRoutes', __name__)

    @ErrorRoutes.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', Error="Bad Request"), 400

    @ErrorRoutes.errorhandler(401)
    def unauthorized(e):
        return render_template('error.html', Error="Unauthorized"), 401

    @ErrorRoutes.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', Error="Forbidden"), 403

    @ErrorRoutes.errorhandler(404)
    def not_found(e):
        return render_template('error.html', Error="Page Not Found"), 404
