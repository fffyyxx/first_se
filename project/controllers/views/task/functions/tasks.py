# coding:utf-8
'''
Created on 2018年5月25日

@author: yuguanc
'''

from __future__ import absolute_import
from celery import shared_task
from controllers.models.libs import Nessus, AWVS11
from ..functions import nessus, awvs
import time
from controllers.models.models import TaskmanageTask, db
# from controllers.views.notices.noticesView import notice_add
from settings.appcelery import celery_out
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery_out.task(ignore_result=True)
def save_scan_vulns(scan_id, task_id):
    task = TaskmanageTask.query.filter_by(Task_id=task_id).first()
    while True:
        res = Nessus.details(scan_id, task.taskmanage_scanner.id)
        try:
            res['info']['status']
        except:
            continue
        if res['info']['status'] == 'canceled' or res['info']['status'] == 'completed':
            nessus.get_scan_vuln(scan_id, task, task.taskmanage_scanner.id)
            task.Taskstatus = '3'
            data = {
                'notice_title': '任务进度通知',
                'notice_body': '您对' + task.Taskname + '的扫描任务已完成，请及时查看结果',
                'notice_url': '/task/user/',
                'notice_type': 'notice',
            }
            user = task.user
            # notice_add(user, data)
            break
        else:
            time.sleep(30)
    db.session.commit()
    return True


@celery_out.task(ignore_result=True)
def save_awvs_vulns(scan_id, task_id):
    task = TaskmanageTask.query.filter_by(task_id=task_id).first()
    while True:
        status = AWVS11.getstatus(scan_id, task.taskmanage_scanner.id)
        if status == 'completed':
            awvs.get_scan_result(scan_id, task_id, task.taskmanage_scanner.id)
            task.task_status = 4
            # type_task_list = {'移动应用':'type1','web应用':'type2','操作系统':'type3'}
            data = {
                'notice_title': '任务进度通知',
                'notice_body': '您对' + task.Taskname + '的扫描任务已完成，请及时查看结果',
                'notice_url': '/task/user/',
                'notice_type': 'notice',
            }
            user = task.task_user
            # notice_add(user, data)
            db.session.commit()
            break
        elif status == 'aborted':
            awvs.get_scan_result(scan_id, task_id, task.taskmanage_scanner.id)
            task.task_status = 5
            # type_task_list = {'移动应用':'type1','web应用':'type2','操作系统':'type3'}
            data = {
                'notice_title': '任务进度通知',
                'notice_body': '您对' + task.Taskname + '的扫描任务已完成，请及时查看结果',
                'notice_url': '/task/user/',
                'notice_type': 'notice',
            }
            user = task.task_user
            # notice_add(user, data)
            break
        else:
            time.sleep(60)
    db.session.commit()
    return True
