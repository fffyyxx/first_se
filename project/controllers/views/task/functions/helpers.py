from ..functions.tasks import save_scan_vulns, save_awvs_vulns
from . import nessus, awvs


def sys_action(task, action):
    nessus_scan = task
    scanner_id = task.taskmanage_scanner.id
    error = None
    if action == 'run':
        scan_id = nessus_scan.Scan_id
        if nessus_scan.Tasktype == '安全扫描':
            do_res = nessus.launch_nessus_scan(scan_id, scanner_id)
        else:
            do_res = True
        if do_res:
            save_scan_vulns.delay(scan_id, task.Task_id)
            # save_scan_vulns(scan_id, task.Task_id)
            nessus_scan.Taskstatus = '2'
        else:
            error = '操作失误，请重试'
    elif action == 'pause':
        scan_id = nessus_scan.Scan_id
        do_res = nessus.pause_nessus_scan(scan_id, scanner_id)
        if do_res:
            nessus_scan.Taskstatus = '4'
        else:
            error = '操作失误，请重试'
    elif action == 'stop':
        scan_id = nessus_scan.Scan_id
        do_res = nessus.stop_nessus_scan(scan_id, scanner_id)
        if do_res:
            nessus_scan.Taskstatus = '4'
        else:
            error = '操作失误，请重试'
    elif action == 'resume':
        scan_id = nessus_scan.Scan_id
        do_res = nessus.resume_nessus_scan(scan_id, scanner_id)
        if do_res:
            nessus_scan.Taskstatus = '2'
        else:
            error = '操作失误，请重试'
    else:
        error = '错误操作指令'
    if error:
        return error
    else:
        return '任务已开启'


def web_action(task, action):
    web_scan = task
    if action == 'run':
        target_id = web_scan.Scan_id
        scan_id = awvs.start_scan(task.taskmanage_scanner.id, target_id)
        web_scan.Taskstatus = '2'
        web_scan.Scan_id = scan_id
        save_awvs_vulns.delay(scan_id, task.Task_id)
        # save_awvs_vulns(scan_id, task)
    elif action == 'stop':
        scan_id = web_scan.scan_id
        res = awvs.stop_scan(scan_id, task.taskmanage_scanner.id)
        if res:
            web_scan.Taskstatus = '4'
    else:
        error = '该类任务暂不支持暂停，请选择取消任务'
        return {'error': error}
    return True
