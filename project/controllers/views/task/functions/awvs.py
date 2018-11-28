# coding:utf-8
"""
Created on 2017/12/4

@author: gy
"""

import time

from controllers.models.libs import AWVS11, parse_awvs_xml
from controllers.models.models import VulnmanageScanvuln, TaskmanageTask, AssetmanageAsset, db
from settings.config import TMP_PATH
from .nessus import Get_except_vuln

vuln_level = {'informational': 0, 'low': 1, 'medium': 2, 'high': 3}


def add_scan(scanner_id, url, desc):
    target_id = AWVS11.add(url, scanner_id, desc)
    return target_id


def start_scan(scanner_id, target_id):
    global scan_id
    data = AWVS11.start(target_id, scanner_id)
    if data:
        scan_id = AWVS11.getscanid(target_id, scanner_id)
    return scan_id


def stop_scan(scan_id, scanner_id):
    data = AWVS11.stop(scan_id, scanner_id)
    if data:
        return True


def dele_scan(scan_id, scanner_id):
    data = AWVS11.delete(scan_id, scanner_id)
    if data:
        return True


def get_scan_result(scan_id, task_id, scanner_id):
    reporturl = AWVS11.getreport(scan_id, scanner_id)
    task = TaskmanageTask.filter_by(Task_id=task_id).first()
    parse_awvs_xml.get_scan_xml(reporturl, scan_id, TMP_PATH)
    details = parse_awvs_xml.details_parse_xml(scan_id, TMP_PATH)
    if details:
        asset_key = details['starturl']
        vuln_list = details['bug']
        asset = AssetmanageAsset.filter_by(Asset_key=asset_key).first()
        if vuln_list:
            except_vuln, except_vuln_list = Get_except_vuln('AWVS')
            for vuln in vuln_list:
                try:
                    num = VulnmanageScanvuln.query.count()
                except Exception as e:
                    num = 0
                vuln_id = '02' + str(time.strftime('%Y%M%d%H', time.localtime(time.time()))) + str(num)
                vuln_type = 'Awvs'
                vuln_name = vuln['name']
                leave = vuln_level[vuln['level']]
                vuln_info = vuln['request']
                introduce = vuln['details']
                scopen = vuln['path']
                fix = vuln['recommendation']
                if vuln_name in except_vuln:
                    vuln_gets = except_vuln_list.filter_by(vuln_name=vuln_name).first()
                    leave = vuln_gets.leave
                    fix = vuln_gets.fix

                vuln_get = VulnmanageScanvuln()

                vuln_get.Vuln_id = vuln_id
                vuln_get.Vuln_name = vuln_name
                vuln_get.Vuln_type = vuln_type
                vuln_get.Leave = leave
                vuln_get.introduce = introduce
                vuln_get.Vuln_info = vuln_info
                vuln_get.Scopen = scopen
                vuln_get.Fix = fix
                vuln_get.Vuln_asset = asset
                vuln_get.task_id = task
                db.session.add(vuln_get)

            db.session.commit()
