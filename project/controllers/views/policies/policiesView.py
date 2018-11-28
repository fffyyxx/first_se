from flask import Blueprint, render_template, request, json, session
from controllers.views.login import login_check
from ..policies.policiesDAL import PoliciesForAll

Policies = Blueprint('Policies', __name__, template_folder='templates', static_folder='static')


@Policies.route('/view/policies')
@login_check
def view_task():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'policies':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('policies/policieslist.html')


@Policies.route('/view/policies_table', methods = ['POST'])
@login_check
def view_policies_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = PoliciesForAll(**dict_a).policies_table()
            return json.dumps(table_list)
        else:
            return json.dumps('')
    except Exception as e:
        print(e)