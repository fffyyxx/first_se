# coding:utf-8
from flask import Blueprint, redirect, url_for, session
from controllers.views.login import login_check
from controllers.views.Frame.FrameDAL import viewmenu, viewusername


Frame = Blueprint('Frame', __name__, template_folder='templates', static_folder='static')


@Frame.route('/', methods=['GET'])
@login_check
def view_frame():
    if "treelist" in session:
        return redirect(url_for('index.view_index'))
    else:
        menu_list = viewmenu(session['loginname'])
        session['treelist'] = menu_list
        session['username'] = viewusername(session['loginname'])
        return redirect(url_for('index.view_index'))


@Frame.route('/Frame')
@login_check
def view_base():
    return redirect(url_for('Frame.view_frame'))
