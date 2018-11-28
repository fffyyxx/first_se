# coding:utf-8
"""
Created on 2017/11/10

@author: gy
"""
from controllers.models.libs import Nessus
import time
from controllers.models.models import VulnmanageScanvuln, AssetmanageAsset, VulnmanageVulnAdvance, db


def Get_except_vuln(vuln_type):
    except_vulns = []
    except_vuln_list = VulnmanageVulnAdvance.query.filter_by(Type=vuln_type).all()
    if except_vuln_list:
        for except_vuln in except_vuln_list:
            except_vulns.append(except_vuln.vuln_name)
    return except_vulns, except_vuln_list


def add_nessus_scan(name, introduce, target, scanner_id, police):
    policies = Nessus.get_policies(scanner_id)
    pid = policies[police]
    scan = Nessus.add(name, introduce, target, pid, scanner_id)
    scan_id = scan['id']
    return scan_id


def launch_nessus_scan(scan_id, scanner_id):
    scan_uuid = Nessus.launch(scan_id, scanner_id)
    return scan_uuid


def pause_nessus_scan(scan_id, scanner_id):
    scan_uuid = Nessus.pause(scan_id, scanner_id)
    return scan_uuid


def resume_nessus_scan(scan_id, scanner_id):
    scan_uuid = Nessus.resume(scan_id, scanner_id)
    return scan_uuid


def stop_nessus_scan(scan_id, scanner_id):
    scan_uuid = Nessus.stop(scan_id, scanner_id)
    return scan_uuid


def get_scan_status(scan_id, scanner_id):
    res = Nessus.details(scan_id, scanner_id)
    return res['info']['status']


def get_scan_vuln(scan_id, task, scanner_id):
    res = Nessus.details(scan_id, scanner_id)
    vuln_list = res.get('vulnerabilities')

    if vuln_list:
        except_vuln, except_vuln_list = Get_except_vuln('Nessus')
        for host in res['hosts']:
            host_id = host['host_id']
            hostname = host['hostname']
            asset_get = AssetmanageAsset.query.filter_by(Asset_key=hostname).first()
            db.session.query(VulnmanageScanvuln).filter_by(Vuln_asset_id=asset_get.id).delete()
            db.session.commit()
            for vuln in vuln_list:
                try:
                    num = VulnmanageScanvuln.query.order_by(VulnmanageScanvuln.id.desc()).first().id
                except Exception as e:
                    num = 0
                num += 1
                vuln_id = '01_' + str(time.strftime('%Y%m%d%H%M', time.localtime(time.time()))) + '_' + str(num)
                vuln_type = 'Nessus'
                vuln_name = vuln.get('plugin_name')
                out_details = Nessus.get_plugin_output(scan_id, host_id, vuln['plugin_id'], scanner_id)
                vuln_info = out_details.get('outputs')
                if vuln_info:
                    if vuln_name in except_vuln:
                        vuln_gets = except_vuln_list.filter_by(vuln_name=vuln_name).first()
                        leave = vuln_gets.leave
                        fix = vuln_gets.fix
                    else:
                        leave = vuln.get('severity')
                        fix = out_details['info']['plugindescription']['pluginattributes']['solution']
                    introduce = out_details['info']['plugindescription']['pluginattributes']['description']
                    scopen = hostname

                    vuln_get = VulnmanageScanvuln()

                    vuln_get.Vuln_id = vuln_id
                    vuln_get.Vuln_name = vuln_name
                    vuln_get.Vuln_type = vuln_type
                    vuln_get.Leave = leave
                    vuln_get.introduce = str(introduce)
                    vuln_get.Vuln_info = str(vuln_info)
                    vuln_get.Scopen = scopen
                    vuln_get.Fix = fix
                    vuln_get.Create_data = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    vuln_get.Update_data = vuln_get.Create_data
                    vuln_get.Vuln_asset_id = asset_get.id
                    db.session.add(vuln_get)
                    db.session.commit()
