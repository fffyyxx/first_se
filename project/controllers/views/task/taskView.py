# coding:utf-8
from flask import Blueprint, render_template, request, json, session
from controllers.views.login import login_check
from ..task.taskDAL import TaskForAll, TaskForRd, TaskForCu

Task = Blueprint('task', __name__, template_folder='templates', static_folder='static')

STATUS_TASK = {'0': '任务状态', '1': '待执行', '2': '执行中', '3': '已结束', '4': '已取消'}
STATUS_REQUEST = {'0': '申请状态', '2': '待审批', '3': '审批通过', '4': '审批拒绝'}


@Task.route('/view/tasks')
@login_check
def view_tasks():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'tasks':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('Task/tasklist.html', data_1=STATUS_TASK, data_2=STATUS_REQUEST)


@Task.route('/view/tasks_table', methods=['POST'])
def view_tasks_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = TaskForAll(**dict_a).task_table()
            json_list = json.dumps(table_list)
            return json_list
        else:
            return json.dumps('')
    except Exception as e:
        print(e)


@Task.route('/view/tasks_curd/<int:id>', methods=['GET', 'DELETE', 'PUT'])  # 查询、删除
@login_check
def view_tasks_rd(id):
    try:
        if request.method == 'GET':
            data = TaskForRd(id, session['user_id']).task_read()
            return render_template('Task/taskdetail.html', data=data)
        elif request.method == 'DELETE':
            data = TaskForRd(id, session['user_id']).task_delete()
            if data == '200':
                return json.dumps(dict(Success=1, Result='删除成功！'))
            else:
                return json.dumps(dict(Success=0, Result='删除失败,信息不存在！'))
        elif request.method == 'PUT':
            data = TaskForRd(id, session['user_id']).task_run()
            return json.dumps(dict(Success=1, Result=data))
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)


@Task.route('/view/tasks_curd', methods=['POST', 'GET'])  # 新增、更新
@login_check
def view_tasks_cu():
    try:
        if request.method == 'GET':
            data_id = request.args.get('id') if request.args.get('id') is not None else 0
            data = TaskForRd(data_id, session['user_id']).task_read()
            return render_template('Task/taskedit.html', data=data)
        elif request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            info_now = TaskForCu(session['user_id'], **dict_a).task_create_or_update()
            return json.dumps(info_now)
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)
