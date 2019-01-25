# coding:utf-8
from flask import Flask
from flask import render_template
from string import digits, ascii_lowercase
from random import sample
from controllers.views.login import loginView
from controllers.views.index.indexView import index
from controllers.views.Frame.FrameView import Frame
from controllers.views.assets.AssetView import Asset
from controllers.views.task.taskView import Task
from controllers.views.vuln.vulnView import Vuln
from controllers.views.scanners.scannersView import Scanners
from controllers.views.policies.policiesView import Policies
from controllers.views.users.userView import User
from controllers.views.roles.roleView import Role
from controllers.views.permissions.permissionView import Permission
from controllers.views.plugin_vuln.plugin_View import Plugin
from controllers.views.login import login_check
from settings.config import ConfigWeb

app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(sample(digits + ascii_lowercase, 10))
app.register_blueprint(loginView)
app.register_blueprint(Frame)
app.register_blueprint(index)
app.register_blueprint(Asset)
app.register_blueprint(Task)
app.register_blueprint(Vuln)
app.register_blueprint(Scanners)
app.register_blueprint(Policies)
app.register_blueprint(User)
app.register_blueprint(Role)
app.register_blueprint(Permission)
app.register_blueprint(Plugin)


@app.errorhandler(404)
@login_check
def page_not_fount(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
@login_check
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.debug = True
    app.run(host=ConfigWeb.WEB_HOST, port=ConfigWeb.WEB_PORT)
