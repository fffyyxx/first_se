from flask import Blueprint, render_template, request, json, session
from controllers.views.login import login_check
from ..scanners.scannersDAL import ScannersForAll

Scanners = Blueprint('Scanners', __name__, template_folder='templates', static_folder='static')


@Scanners.route('/view/scanners')
@login_check
def view_task():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'scanners':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('scanners/scannerslist.html')


@Scanners.route('/view/scanners_table', methods = ['POST'])
@login_check
def view_scanners_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = ScannersForAll(**dict_a).scanners_table()
            return json.dumps(table_list)
        else:
            return json.dumps('')
    except Exception as e:
        print(e)