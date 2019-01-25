#!/usr/bin/env python3
# License: GPL-3.0

from ssl import SSLContext
from flask import Flask, render_template,request
from flask_login import login_required, current_user
from server.config import CERT_FILE, KEY_FILE, EXTERNALIP, SSL_VERSION
from server.db import post_command, clear_db, init_db, admin_login, update_admin, admin_logout

from server.AdminServer.core.login import Login
from server.AdminServer.core.error import Error
from server.AdminServer.core.api import API

##################################################################
# Flask Application Class
##################################################################
class AdminServer(object):

    app = Flask(__name__)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    # Initialize Modules
    Login(app)
    Error(app)
    API(app)

    def __init__(self):
        # Set SSL/TLS context & start dev HTTP server (FYI: This is not a full WSGI)
        context = SSLContext(SSL_VERSION)
        context.load_cert_chain(CERT_FILE, KEY_FILE)
        self.app.run(host='0.0.0.0', port=8443, ssl_context=context, threaded=True)

    ##################################################################
    # Main
    ##################################################################
    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def run():
        return render_template('admin.html')

    ##################################################################
    # User Modification Pages to interact with DB
    ##################################################################
    @app.route('/add_admin', methods=['GET', 'POST'])
    @login_required
    def add_admin():
        if request.method == 'POST':
            if request.form['password'] == request.form['password2']:
                update_admin(request.form['username'], request.form['password'], "Inactive")
                return render_template('success.html')
            else:
                return render_template('fail.html')
        return render_template('add_admin.html')

    @app.route('/change_pwd', methods=['GET', 'POST'])
    @login_required
    def change_pwd():
        if request.method == 'POST':
            if request.form['password'] == request.form['password2']:
                update_admin(current_user, request.form['password'], "Active")
                return render_template('success.html')
            else:
                return render_template('fail.html')
        return render_template('change_pwd.html', data=current_user)