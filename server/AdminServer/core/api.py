#!/usr/bin/env python3
# License: GPL-3.0

from json import dumps
from flask import Flask, render_template, request, Response, Blueprint, send_from_directory,Markup
from flask_login import login_required, current_user
from server.db import active_clients, active_admins, cmd_log, post_command, clear_pending, update_results
from decimal import Decimal
from server.AdminServer.core.loader import get_help, list_modules, exec_module
from server.config import cmd_encode, cmd_decode

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
            obj['Command'] = cmd_decode(x[3])
            obj['Response'] = cmd_decode(x[4])
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
        c_input = request.form.getlist('clients')   # Get list of clients from form
        cmd = request.form['command']               # Extract cmd from form
        # Reformat clients from JS input
        try:
            clients = c_input[0].split(',')
        except:
            clients = c_input[0]
        # Begin checks of execution
        for c in clients:
            if c and cmd:
                # clientid:type / "1:py"
                cid, type = c.split(":")
                try:
                    for mod, class_obj in list_modules().items():
                        # Check for module execution
                        if cmd.startswith(mod):
                            # Verify language is supported by module & client
                            if type in class_obj.language:
                                cmd = exec_module(mod, cmd)
                            else:
                                raise Exception("The client type does not support this module")
                        # Encode and Send cmd to DB for execution
                        post_command(cid, current_user, cmd_encode(cmd))
                except Exception as e:
                    print(e)
                    # Close CMD and report error to user
                    post_command(cid, current_user, cmd_encode(cmd))
                    update_results(cid, cmd_encode("Server Error: {}".format(str(e))))
        return render_template('admin.html', data=Markup(get_help()))

    @APIRoutes.route('/api/clear', methods=['GET'])
    @login_required
    def api_clear():
        ## Clear pending commands
        clear_pending()
        return render_template('admin.html', data=Markup(get_help()))

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