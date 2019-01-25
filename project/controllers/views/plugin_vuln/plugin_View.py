from flask import Blueprint, render_template, request, json, session, Flask, redirect, url_for, make_response
from controllers.views.login import login_check
from views import Mongo, page_size, app
from urllib import parse
from views.lib.QueryLogic import querylogic
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from views.lib.CreateExcel import write_data
import os
from Config import ProductionConfig

Plugin = Blueprint('plugin', __name__, template_folder='templates', static_folder='static')


# 搜索界面
@Plugin.route('/filter')
@login_check
def Search():
    return render_template('search.html')


# 搜索结果界面
@Plugin.route('/233')
@login_check
def Main():
    q = request.args.get('q', '')
    page = int(request.args.get('page', '1'))
    plugin = Mongo.coll['Plugin'].find()  # 插件列表
    plugin_type = plugin.distinct('type')  # 插件类型列表
    if q:  # 基于搜索条件显示结果
        result = q.strip().split(';')
        query = querylogic(result)
        cursor = Mongo.coll['Info'].find(query).sort('time', -1).limit(page_size).skip((page - 1) * page_size)
        return render_template('main.html', item=cursor, plugin=plugin, itemcount=cursor.count(),
                               plugin_type=plugin_type, query=q)
    else:  # 自定义，无任何结果，用户手工添加
        return render_template('main.html', item=[], plugin=plugin, itemcount=0, plugin_type=plugin_type)


# 插件库界面
@Plugin.route('/plugin')
@login_check
def Plugins():
    page = int(request.args.get('page', '1'))
    cursor = Mongo.coll['Plugin'].find().limit(page_size).skip((page - 1) * page_size)
    return render_template('plugin.html', cursor=cursor, vultype=cursor.distinct('type'), count=cursor.count())


@Plugin.route('/getplugin', methods=['get', 'post'])
@login_check
def Getplugin():
    type = request.form.get('type', '')
    risk = request.form.get('risk', '')
    search = request.form.get('search', '')
    query = {}
    if type:
        query['type'] = type
    if risk:
        query['level'] = risk
    if search:
        search = parse.unquote(search)
        query['name'] = {"$regex": search, '$options': 'i'}
    cursor = Mongo.coll['Plugin'].find(query)
    rsp = []
    for i in cursor:
        result = {'name': i['name'], 'info': i['info']}
        rsp.append(result)
    return json.dumps(rsp)


# 任务列表界面
@Plugin.route('/task')
@login_check
def Task():
    page = int(request.args.get('page', '1'))
    cursor = Mongo.coll['Task'].find().sort('time', -1).limit(page_size).skip((page - 1) * page_size)
    return render_template('task.html', item=cursor)


# 添加任务界面
@Plugin.route('/addtask', methods=['get', 'post'])
@login_check
def Addtask():
    title = request.form.get('title', '')
    plugin = request.form.get('plugin', '')
    condition = parse.unquote(request.form.get('condition', ''))
    plan = request.form.get('plan', 0)
    ids = request.form.get('ids', '')
    isupdate = request.form.get('isupdate', '0')
    resultcheck = request.form.get('resultcheck', '0')
    result = 'fail'
    if plugin:
        targets = []
        if resultcheck == 'true':  # 结果集全选
            list = condition.strip().split(';')
            query = querylogic(list)
            cursor = Mongo.coll['Info'].find(query)
            for i in cursor:
                tar = [i['ip'], i['port']]
                targets.append(tar)
        else:  # 当前页结果选择
            for i in ids.split(','):
                tar = [i.split(':')[0], int(i.split(':')[1])]
                targets.append(tar)
        temp_result = True
        for p in plugin.split(','):
            query = querylogic(condition.strip().split(';'))
            item = {'status': 0, 'title': title, 'plugin': p, 'condition': condition, 'time': datetime.now(),
                    'target': targets, 'plan': int(plan), 'isupdate': int(isupdate), 'query': dumps(query)}
            insert_reuslt = Mongo.coll['Task'].insert(item)
            if not insert_reuslt:
                temp_result = False
        if temp_result:
            result = 'success'
    return result


# 任务复查
@Plugin.route('/taskrecheck')
@login_check
def Recheck():
    tid = request.args.get('taskid', '')
    task = Mongo.coll['Task'].find_one({'_id': ObjectId(tid)})
    result = 'fail'
    if task and task['plan'] == 0 and task['status'] == 2:  # 一次性任务，并且已经扫描完成
        result = Mongo.coll['Task'].update({'_id': ObjectId(tid)}, {'$set': {'status': 0}})
        if result:
            result = 'success'
    return result


# 任务详情
@Plugin.route('/taskdetail')
@login_check
def TaskDetail():
    id = request.args.get('taskid', '')
    page = int(request.args.get('page', '1'))
    taskdate = request.args.get('taskdate', "")
    plugin_name = ''
    task_info = Mongo.coll['Task'].find_one({'_id': ObjectId(id)})
    if task_info:
        plugin_name = task_info['plugin']
    vulcount = 0
    lastscan = Mongo.coll["Result"].distinct('task_date', {'task_id': ObjectId(id)})
    result_list = []
    if len(lastscan) > 0:
        lastscan.sort(reverse=True)
        if taskdate:  # 根据扫描批次查看结果
            cursor = Mongo.coll['Result'].find(
                {'task_id': ObjectId(id), 'task_date': datetime.strptime(taskdate, "%Y-%m-%d %H:%M:%S.%f")}).sort(
                'time', -1).limit(page_size).skip((page - 1) * page_size)
        else:  # 查看最新批次结果
            taskdate = lastscan[0].strftime("%Y-%m-%d %H:%M:%S.%f")
            cursor = Mongo.coll['Result'].find(
                {'task_id': ObjectId(id), 'task_date': lastscan[0]}).sort('time', -1).limit(page_size).skip(
                (page - 1) * page_size)
        vulcount = cursor.count()
        for _ in cursor:
            result_list.append(
                {'ip': _['ip'], 'port': _['port'], 'info': _['info'], 'vul_level': _['vul_info']['vul_level'],
                 'time': _['time']})

        # 速度优化，数据量多采取不同的方式查询
        if len(result_list) > 100:
            ip_hostname = {}
            hostname = Mongo.coll['Info'].aggregate(
                [{'$match': {'hostname': {'$ne': None}}}, {'$project': {'_id': 0, 'ip': 1, 'hostname': 1}}])
            for _ in hostname:
                if 'hostname' in hostname:
                    ip_hostname[_["ip"]] = _["hostname"]
            for _ in result_list:
                if 'ip' in ip_hostname:
                    _['hostname'] = ip_hostname[_["ip"]]
                else:
                    _['hostname'] = ''
        else:
            for _ in result_list:
                hostname = Mongo.coll['Info'].find_one({'ip': _['ip']})
                if hostname and 'hostname' in hostname:
                    _['hostname'] = hostname['hostname']
                else:
                    _['hostname'] = ''
    return render_template('detail.html', item=result_list, count=vulcount, id=id, taskdate=taskdate,
                           plugin_name=plugin_name, scanlist=lastscan)


@Plugin.route('/deletetask', methods=['get', 'post'])
@login_check
def DeleteTask():
    oid = request.form.get('oid', '')
    if oid:
        result = Mongo.coll['Task'].delete_one({'_id': ObjectId(oid)})
        if result.deleted_count > 0:
            result = Mongo.coll['Result'].delete_many({'task_id': ObjectId(oid)})
            if result:
                return 'success'
    return 'fail'


# 搜索结果下载接口
@Plugin.route('/searchxls', methods=['get'])
@login_check
def search_result_xls():
    query = request.args.get('query', '')
    if query:
        result = query.strip().split(';')
        filter_ = querylogic(result)
        cursor = Mongo.coll['Info'].find(filter_).sort('time', -1)
        title_tup = ('IP', '端口号', '主机名', '服务类型')
        xls = [title_tup, ]
        for info in cursor:
            item = (
                info.get('ip'), info.get('port'),
                info.get('hostname'), info.get('server')
            )
            xls.append(item)
        file = write_data(xls, 'search_result')
        resp = make_response(file.getvalue())
        resp.headers["Content-Disposition"] = "attachment; filename=search_result.xls;"
        resp.headers["Content-Type"] = "application/x-xls"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp
    else:
        redirect(url_for('NotFound'))