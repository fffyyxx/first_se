# coding:utf-8
from flask import Blueprint, render_template
from controllers.views.login import login_check
from controllers.views.index.indexDAL import index_info


index = Blueprint('index', __name__, template_folder='templates', static_folder='static')


@index.route('/index')
@login_check
def view_index():
    all_count = index_info()
    return render_template('index.html', all_info=all_count)


