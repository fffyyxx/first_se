from flask import Blueprint, render_template, request, json, session
from controllers.views.login import login_check
from ..vuln.vulnDAL import VulnForAll, LoopholeForAll, LoopholeForRd
import os

Vuln = Blueprint('vuln', __name__, template_folder='templates', static_folder='static')

LEVEL_FOR_VULN = {
    '-1': '请选择危险等级',
    '0': '常规',
    '1': '低危',
    '2': '中危',
    '3': '高危',
    '4': '紧急'
}


@Vuln.route('/view/scanvuln')
@login_check
def view_scanvuln():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'scanvuln':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('Vuln/vulnscanlist.html', data=LEVEL_FOR_VULN)


@Vuln.route('/view/vulnmanage')
@login_check
def view_vulnmanage():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'vulnmanage':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('Vuln/vulnlist.html')


@Vuln.route('/view/vulnscan_table', methods=['POST'])
@login_check
def view_scanvuln_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = VulnForAll(**dict_a).vuln_table()
            json_list = json.dumps(table_list)
            return json_list
        else:
            return json.dumps('')
    except Exception as e:
        print(e)


@Vuln.route('/view/vulnmanage_table', methods=['POST'])
@login_check
def view_vulnmange_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = LoopholeForAll(**dict_a).loophole_table()
            return json.dumps(table_list)
        else:
            return json.dumps('')
    except Exception as e:
        print(e)


@Vuln.route('/view/vulnmanage_curd/<int:id>', methods=['GET', 'DELETE'])
@login_check
def view_loopholevuln_rd(id):
    try:
        if request.method == 'GET':
            data = LoopholeForRd(id).loophole_read()
            if data == '404':
                return render_template('404.html'), 404
            else:
                return render_template('Vuln/vulndetail.html', data=data)
        elif request.method == 'DELETE':
            data = LoopholeForRd(id).loophole_delete()
            if data == '200':
                return json.dumps(dict(Success=1, Result='删除成功！'))
            else:
                return json.dumps(dict(Success=0, Result='删除失败！'))
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)


@Vuln.route('/view/vulnmanage/spider', methods=['PUT'])
@login_check
def view_loopholevuln_spider():
    try:
        if request.method == 'PUT':
            os.system('d:')
            os.chdir('D:\yangxaio\HENGTONG\icnnvd\icnnvd\spiders')
            p = os.popen('dir')
            print(p.read())
            os.system('scrapy crawl mycnnvd')
            return json.dumps(dict(Success=1, Result='更新成功！'))
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)
