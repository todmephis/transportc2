#!/usr/bin/env python3
# License: GPL-3.0

from json import dumps
from flask import Flask, render_template, session, redirect, url_for, escape, request, Response, Blueprint
from flask_login import login_required, current_user
from server.db import active_clients, active_admins, cmd_log, post_command, clear_pending

##################################################################
#
# Auto refresh data tables in html through API
#
##################################################################
class API(object):

    def __init__(self, app):
        app.register_blueprint(self.APIRoutes)


    APIRoutes = Blueprint('APIRoutes', __name__)


    @APIRoutes.route('/api/log', methods=['GET'])
    def api_log():
        DATA = []
        for x in cmd_log():
            obj = {}
            obj['User']= x[0]
            obj['Agent'] = x[1]
            obj['Time'] = x[2]
            obj['Command'] = x[3]
            obj['Response'] = x[4]
            DATA.append(obj)
        return Response(response=dumps(DATA, default=default), status=200, mimetype='application/json')

    @APIRoutes.route('/api/client', methods=['GET'])
    def api_client():
        DATA = []
        for x in active_clients():
            obj = {}
            obj['Agent']= x
            DATA.append(obj)
        return Response(response=dumps(DATA, default=default), status=200, mimetype='application/json')

    @APIRoutes.route('/api/admin', methods=['GET'])
    def api_admin():
        DATA = []
        for x in active_admins():
            obj = {}
            obj['User'] = x
            DATA.append(obj)
        return Response(response=dumps(DATA, default=default), status=200, mimetype='application/json')

    @APIRoutes.route('/api/cmd', methods=['POST'])
    @login_required
    def api_cmd():
        ## Admin Form Submission
        post_command(current_user, request.form['hostname'],request.form['command'])
        return render_template('admin.html')

    @APIRoutes.route('/api/clear', methods=['GET'])
    @login_required
    def api_clear():
        ## Clear pending commands
        clear_pending()
        return render_template('admin.html')

def default(obj):
    # This function is used as the default encoder for api controller - IDK what this does but it breaks without it
    if isinstance(obj, Decimal):
        return float(obj)
    else:
        return str(obj)
    raise TypeError