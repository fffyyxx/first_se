# coding:utf-8
from controllers.models.models import TaskmanageTask, TaskmanageScanner, TaskmanageScannerpolicy
from controllers.models.models import AssetmanageAsset, User, db
from ..task.functions.helpers import sys_action, web_action
from sqlalchemy import or_
import time

from controllers.views.task.functions import nessus, awvs


class TaskForAll(object):

    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']
        self.user_id = int(kwargs['user_id'])
        self.is_admin = int(kwargs['is_admin'])
        self.task_status = str(kwargs['task_status'])
        self.request_status = str(kwargs['request_status'])

    def task_table(self):
        global counts, task_dict, task_list
        counts = 0
        task_dict = {}
        task_list = []

        page_num = int(self.offset) / int(self.limit) + 1
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        # 搜索设置
        task_data = TaskmanageTask.query. \
            filter(or_(TaskmanageTask.Taskname.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '',
                       TaskmanageTask.Tasktarget.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '')). \
            order_by(TaskmanageTask.id.desc())

        if self.task_status != '0':
            task_data = task_data.filter(TaskmanageTask.Taskstatus == self.task_status)
        if self.request_status != '0':
            task_data = task_data.filter(TaskmanageTask.Requeststatus == self.request_status)
        if self.is_admin != 1:
            task_data = task_data.filter(TaskmanageTask.Taskuserid == self.user_id)

        task_items = task_data.paginate(int(page_num), per_page=self.limit, error_out=False).items
        counts = task_data.count()

        for item in task_items:
            task_dict[item.id] = {}
            task_dict[item.id]['id'] = item.id
            task_dict[item.id]['task_id'] = item.Task_id
            task_dict[item.id]['taskname'] = item.Taskname
            task_dict[item.id]['tasktarget'] = item.Tasktarget
            task_dict[item.id]['taskstatus'] = item.Taskstatus
            task_dict[item.id]['requeststatus'] = item.Requeststatus
            task_dict[item.id]['createtime'] = item.Createtime.strftime('%Y-%m-%d %H:%M:%S')
            task_dict[item.id]['taskusername'] = item.user1.UserName
            task_dict[item.id]['taskuserid'] = item.user1.id
            task_dict[item.id]['auditname'] = item.user.UserName
            task_dict[item.id]['audituserid'] = item.user.id
            task_list.append(task_dict[item.id])

        return {'total': counts, 'rows': task_list}


class TaskForRd(object):

    def __init__(self, data_id, sysuser_id):
        self.id = data_id
        self.actionid = int(sysuser_id)

    def task_read(self):
        global data, taskpolicy
        data = {}
        taskpolicy = {}

        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题

        model_user = User.query.filter_by(id=self.actionid).first()
        model = TaskmanageTask.query.filter_by(id=int(self.id)).first()
        model_policy = TaskmanageScannerpolicy.query.all()
        for p in model_policy:
            taskpolicy[p.id] = p.Policiesname
        if model:
            data = {
                'task_id': model.Task_id,
                'taskname': model.Taskname,
                # 'taskscanner': model.taskmanage_scanner.Scannername,
                'tasktarget': model.Tasktarget,
                'tasktargetinfo': model.Tasktargetinfo,
                'taskstatus': model.Taskstatus,
                'requeststatus': model.Requeststatus,
                'createtime': model.Createtime.strftime('%Y-%m-%d %H:%M:%S'),
                'taskusername': model.user1.UserName,
                'taskuserid': model.user1.id,
                'taskpolicy': model.taskmanage_scannerpolicy.Policiesname,
                'taskpolicyid': model.taskmanage_scannerpolicy.id,
                'taskpolicysel': '',
                'auditname': model.user.UserName,
                'audittime': model.Audittime.strftime('%Y-%m-%d %H:%M:%S') if model.Audittime is not None else '',
                'auditinfo': model.Auditinfo if model.Auditinfo is not None else ''
            }
        else:
            data = {
                'task_id': 's' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())),
                'taskname': '',
                # 'taskscanner': '',
                'tasktarget': '',
                'tasktargetinfo': '',
                'taskstatus': '1',
                'requeststatus': '1',
                'createtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                'taskusername': model_user.UserName,
                'taskuserid': model_user.id,
                'taskpolicy': '请选择',
                'taskpolicyid': 0,
                'taskpolicysel': taskpolicy
            }

        return data

    def task_delete(self):
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        model = TaskmanageTask.query.filter_by(id=self.id).first()
        if model:
            db.session.delete(model)
            db.session.commit()
            return '200'
        else:
            return '404'

    def task_run(self):
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        global res
        res = ''
        task = TaskmanageTask.query.filter_by(id=self.id).first()
        if task.taskmanage_scanner.Scannertype == 'Nessus':
            res = sys_action(task, 'run')
        elif task.taskmanage_scanner.Scannertype == 'AWVS':
            res = web_action(task, 'run')
        elif task.taskmanage_scanner.Scannertype == 'MobSF':
            res = '本功能暂不开放'
        return res


class TaskForCu(object):
    dict_model = dict(success=0, result='')

    def __init__(self, audit_userid, **kwargs):
        self.taskid = kwargs['task_id']
        self.taskname = kwargs['taskname'] if 'taskname' in kwargs.keys() else ''
        self.tasktarget = kwargs['tasktarget'] if 'tasktarget' in kwargs.keys() else ''
        self.tasktargetinfo = kwargs['tasktargetinfo'] if 'tasktargetinfo' in kwargs.keys() else ''
        self.taskscanpolicy = kwargs['taskscanpolicy'] if 'taskscanpolicy' in kwargs.keys() else ''
        self.taskuserid = kwargs['taskuserid'] if 'taskuserid' in kwargs.keys() is not None else ''
        self.auditinfo = kwargs['auditinfo'] if 'auditinfo' in kwargs.keys() is not None else ''
        self.auditstatus = kwargs['auditstatus']
        self.auditaction = kwargs['auditaction']
        self.audituserid = audit_userid

    def task_create_or_update(self):
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        model_add = TaskmanageTask()

        global scan_id, statusinfo
        scan_id = ''
        statusinfo = TaskForCu.dict_model
        user = User.query.filter_by(id=int(self.audituserid)).first()
        task = TaskmanageTask.query.filter_by(Task_id=self.taskid).first()
        if task:
            model_add = task
            if self.auditaction == '0':
                model_add.Requeststatus = '4'
                model_add.Taskstatus = '4'
            else:
                if self.auditstatus == '1':
                    model_add.Requeststatus = '2'
                    model_add.Taskstatus = '1'
                elif self.auditstatus == '2':
                    model_add.Requeststatus = '3'
                    model_add.Taskstatus = '1'
            model_add.Auditinfo = self.auditinfo
            model_add.Audittime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            model_add.Audituserid = int(self.audituserid)
            statusinfo['success'] = 1
            statusinfo['result'] = '审核完成!'
        else:
            model_add.Task_id = self.taskid
            model_add.Taskname = self.taskname
            model_add.Tasktarget = self.tasktarget
            model_add.Tasktargetinfo = self.tasktargetinfo
            model_add.Taskuserid = int(self.taskuserid)
            model_add.Tasktype = '安全扫描'
            model_add.Createtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            task_policy = TaskmanageScannerpolicy.query.filter_by(id=int(self.taskscanpolicy)).first()
            model_add.Scannerpoliceid = task_policy.id

            task_scanner = task_policy.Scanner
            model_add.Taskscannerid = task_scanner.id

            task_asset = AssetmanageAsset.query.filter_by(Asset_key=self.tasktarget).first()
            if task_asset:
                if task_scanner.Scannertype == 'Nessus':
                    scan_id = nessus.add_nessus_scan(self.taskname, self.tasktargetinfo, self.tasktarget,
                                                     task_scanner.id,
                                                     task_policy.Policiesname)
                elif task_scanner.Scannertype == 'AWVS':
                    scan_id = awvs.add_scan(task_scanner.id, self.tasktarget, self.tasktargetinfo)
                if scan_id != 'error':
                    model_add.Requeststatus = '2'
                    model_add.Taskstatus = '1'
                    model_add.Scan_id = int(scan_id)

                    if user.IsAdmin == 1:
                        model_add.Requeststatus = '3'
                        model_add.Audituserid = user.id
                        model_add.Audittime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        model_add.Auditinfo = '审核通过'
                    else:
                        useradmin = User.query.fliter_by(IsAdmin=1).first()
                        model_add.Audituserid = useradmin.id

                    db.session.add(model_add)

                    statusinfo['success'] = 1
                    statusinfo['result'] = '添加成功!'
                else:
                    statusinfo['success'] = 0
                    statusinfo['result'] = '目标地址或设备无法被本次扫描识别!'
            else:
                statusinfo['success'] = 0
                statusinfo['result'] = '目标地址不在设备列表中!'

        db.session.commit()
        return statusinfo
