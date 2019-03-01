#!/usr/bin/env python3
# License: GPL-3.0

from json import dumps
from decimal import Decimal
from server.config import cmd_encode, cmd_decode
from flask_login import login_required, current_user
from flask import Flask, render_template, request, Response, Blueprint, send_from_directory,Markup
from server.db import active_clients, active_admins, cmd_log, post_command, clear_pending, update_results, db_connect

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
        con = db_connect()
        for x in cmd_log(con):
            obj = {}
            obj['User']= x[0]
            obj['Agent'] = x[1]
            obj['Time'] = x[2]
            obj['Command'] = cmd_decode(x[3]).splitlines()[0]
            obj['Response'] = cmd_decode(x[4]).strip()
            DATA.append(obj)
        con.close()
        return Response(response=dumps(DATA, default=default), status=200, mimetype='application/json')

    @APIRoutes.route('/api/client', methods=['GET'])
    def api_client():
        con = db_connect()
        c = active_clients(con)
        con.close()
        return Response(response=dumps(c, default=default), status=200, mimetype='application/json')

    @APIRoutes.route('/api/admin', methods=['GET'])
    def api_admin():
        DATA = []
        con = db_connect()
        for x in active_admins(con):
            obj = {}
            obj['User'] = x
            DATA.append(obj)
        con.close()
        return Response(response=dumps(DATA, default=default), status=200, mimetype='application/json')

    @APIRoutes.route('/api/cmd', methods=['POST'])
    @login_required
    def api_cmd():
        ## Admin Form Submission
        c_input = request.form.getlist('clients')   # Get list of clients from form
        cmd = request.form['command'].strip()               # Extract cmd from form

        # Reformat clients from JS input
        try:
            clients = c_input[0].split(',')
        except:
            clients = c_input[0]

        con = db_connect()

        # Begin checks of execution
        for c in clients:
            if c and cmd:
                # clientid:type / "1:py"
                cid, type = c.split(":")
                try:
                    # Encode and Send cmd to DB for execution
                    post_command(con, cid, current_user, cmd_encode(cmd))
                except Exception as e:
                    print(e)
                    # Close CMD and report error to user
                    post_command(con, cid, current_user, cmd_encode(cmd))
                    update_results(con, cid, cmd_encode("Server Error: {}".format(str(e))))
        con.close()
        return render_template('admin.html')

    @APIRoutes.route('/api/clear', methods=['GET'])
    @login_required
    def api_clear():
        ## Clear pending commands
        con = db_connect()
        clear_pending(con)
        con.close()
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