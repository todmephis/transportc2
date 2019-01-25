#!/usr/bin/env python3
# License: GPL-3.0

from server.db import admin_login, admin_logout
from flask import redirect, request, Blueprint, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

##################################################################
#
# User Login
#
##################################################################

# User model
class User(UserMixin):
    # Thank you: https://github.com/shekhargulati/flask-login-example/blob/master/flask-login-example.py
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "%s" % (self.id)

    # flask-login
class Login(object):

    login_manager = LoginManager()
    login_manager.login_view = "LoginRoutes.login"

    def __init__(self,app):
        self.app=app
        self.login_manager.init_app(app)
        app.register_blueprint(self.LoginRoutes)

    # callback to reload the user object
    @login_manager.user_loader
    def load_user(userid):
        return User(userid)

    LoginRoutes = Blueprint('LoginRoutes', __name__)

    @LoginRoutes.route('/login', methods=['GET', 'POST'])
    def login():
        ## Admin Form Submission
        if request.method == 'POST':
                # Validate
                if admin_login(request.form['username'], request.form['password']):
                    user = User(request.form['username'])
                    login_user(user, remember=False)
                    return redirect("/",302)
                else:
                    render_template('login.html')
        else:
            return render_template('login.html')


    # somewhere to logout
    @LoginRoutes.route("/logout")
    @login_required
    def logout():
        admin_logout(current_user)
        logout_user()
        return redirect("/", 302)
