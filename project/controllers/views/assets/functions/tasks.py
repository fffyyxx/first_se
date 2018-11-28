# coding:utf-8
import time
from controllers.models.libs import nmap
from controllers.models.models import AssetmanageAsset, AssetmanageAssetPort, User, db
# from controllers.views.notices import notice_add
from celery.utils.log import get_task_logger
from controllers.models.libs.checkip import checkip
from settings.appcelery import celery_out

logger = get_task_logger(__name__)


@celery_out.task(ignore_result=True)
def asset_port(user_id, ip_address):
    user = User.query.filter_by(id=user_id).first()
    global data_manage
    data_manage = {}
    for item in ip_address:
        ip_id = item
        asset = AssetmanageAsset.query.filter_by(Asset_key=ip_id).first()
        port_asset = AssetmanageAssetPort.query.filter_by(Asset_id=ip_id).all()
        if asset:
            ip = asset.Asset_key
            if checkip(ip):
                port_list = nmap.nmap_host_all(ip)
                if port_list != 0:
                    for port_info in port_list.keys():
                        model_info = AssetmanageAssetPort()
                        model_info.Port = port_info
                        model_info.Requestname = port_list[port_info].get('name')
                        model_info.Product = port_list[port_info].get('product')
                        model_info.Version = port_list[port_info].get('version')
                        model_info.Updatetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        model_info.Asset_id = asset.id

                        if port_info not in port_asset:
                            db.session.add(model_info)

                    for info_port in port_asset:
                        if info_port.Port not in port_list.keys():
                            db.session.delete(info_port)
                    data_manage = {
                        'notice_title': '资产发现通知',
                        'notice_body': '您对' + ip + '的端口发现任务完成',
                        'notice_url': '/asset/user/',
                        'notice_type': 'notice',
                    }
                else:
                    data_manage = {
                        'notice_title': '资产发现通知',
                        'notice_body': '您对' + ip + '的端口发现任务完成,该主机未开放端口或网络不可达',
                        'notice_url': '/asset/user/',
                        'notice_type': 'notice',
                    }
                db.session.commit()
                # notice_add(user, data_manage)
            else:
                return False
        else:
            return False

    return True


@celery_out.task(ignore_result=True)
def asset_descover(user_id, ip_address):
    user = User.query.filter_by(id=user_id).first()
    global data_manage
    data_manage = {
        'notice_title': '资产发现通知',
        'notice_body': '您的资产发现任务已开始，请勿重复提交',
        'notice_url': '/asset/user/',
        'notice_type': 'notice',
    }
    # notice_add(user, data_manage)
    # for item in ip_address:
    ip_id = ip_address
    if len(ip_id.split('/')) > 1:
        segment = ip_id
        host_list = nmap.nmap_alive_lists(segment)
        if host_list is None:
            data_manage = {
                'notice_title': '资产发现通知',
                'notice_body': '针对网段' + segment + '的资产扫描任务已完成，网络不可达或无存活主机',
                'notice_url': '/asset/user/',
                'notice_type': 'notice',
            }
            # notice_add(user, data_manage)
        else:
            global num_id
            num_id = 0
            for host in host_list:
                num_id += 1
                asset_get = AssetmanageAsset.query.filter_by(Asset_key=host).first()
                if asset_get is None:
                    model = AssetmanageAsset()
                    index_key = '01' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + str(num_id)
                    model.Asset_num = index_key
                    model.Assert_name = '设备_' + index_key
                    model.Asset_key = host
                    model.Asset_type = '设备'
                    model.Asset_user = user.LoginName
                    model.Asset_status = '1'
                    model.Asset_registertime = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
                    # asset_get.Asset_updatetime = model.Asset_registertime
                    model.Asset_updatetime = model.Asset_registertime   # 修改过
                    db.session.add(model)
                else:
                    asset_get.Asset_updatetime = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
            db.session.commit()
    else:
        return False

    data_manage = {
        'notice_title': '资产发现通知',
        'notice_body': '您的资产发现任务已完成，请注意查看',
        'notice_url': '/asset/user/',
        'notice_type': 'notice',
    }
    # notice_add(user, data_manage)
    return True
