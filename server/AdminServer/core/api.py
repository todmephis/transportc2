#!/usr/bin/env python3
# License: GPL-3.0

from json import dumps
from flask import Flask, render_template, request, Response, Blueprint, send_from_directory
from flask_login import login_required, current_user
from server.db import active_clients, active_admins, cmd_log, post_command, clear_pending
from base64 import b64decode, b64encode
from decimal import Decimal

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
            obj['Command'] = b64decode(x[3]).decode('utf-8')
            obj['Response'] = b64decode(x[4]).decode('utf-8')
            DATA.append(obj)
        return Response(response=dumps(DATA, default=default), status=200, mimetype='application/json')

    @APIRoutes.route('/api/client', methods=['GET'])
    def api_client():
        return Response(response=dumps(active_clients(), default=default), status=200, mimetype='application/json')

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
        clients = request.form.getlist('clients')
        cmd = request.form['command']
        if cmd:
            encoded_cmd = b64encode(cmd.encode('utf-8')).decode('utf-8')
            for cid in clients[0]:
                try:
                    post_command(int(cid), current_user, encoded_cmd)
                except:
                    pass
        return render_template('admin.html')

    @APIRoutes.route('/api/clear', methods=['GET'])
    @login_required
    def api_clear():
        ## Clear pending commands
        clear_pending()
        return render_template('admin.html')

    @APIRoutes.route('/api/master_log', methods=['GET'])
    @login_required
    def api_masterlog():
        return send_from_directory('../../logs/','master_log.txt')

def default(obj):
    # This function is used as the default encoder for api controller - IDK what this does but it breaks without it
    if isinstance(obj, Decimal):
        return float(obj)
    else:
        return str(obj)
    raise TypeError