# coding:utf-8
from controllers.models.models import AssetmanageAsset, VulnmanageScanvuln, AssetmanageAssetPort, AssetmanageAssetO, \
    AssetmanageAssetFile, db
from controllers.views.assets.functions.tasks import asset_port, asset_descover
from sqlalchemy import or_

ASSET_STATUS = {
    '0': '使用中',
    '1': '闲置中',
    '2': '已销毁',
}

LEVEL_FOR_VULN = {
    '0': '常规',
    '1': '低危',
    '2': '中危',
    '3': '高危',
    '4': '紧急'
}

dict_model = dict(success=1, result='')


class AssetForAll(object):

    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']
        self.username = kwargs['username']
        self.asset_status = kwargs['asset_status']
        self.is_admin = int(kwargs['is_admin'])

    def asset_table(self):
        db.session.commit()  # 解决程序以及数据库层面带来的缓存问题
        global counts, asset_list, list_dict
        counts = 0
        asset_list = []
        list_dict = {}

        page_num = int(self.offset) / int(self.limit) + 1

        asset_data = AssetmanageAsset.query.filter(
            or_(AssetmanageAsset.Assert_name.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '',
                AssetmanageAsset.Asset_key.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '')). \
            order_by(AssetmanageAsset.id.desc())

        if self.asset_status != '0':
            asset_data = asset_data.filter(AssetmanageAsset.Asset_status == self.asset_status)
        if self.is_admin != 1:
            asset_data = asset_data.filter(AssetmanageAsset.Asset_user == self.username)

        asset_items = asset_data.paginate(int(page_num), per_page=self.limit, error_out=False).items

        counts = asset_data.count()

        for item in asset_items:
            list_dict[item.id] = {}
            list_dict[item.id]['id'] = item.id
            list_dict[item.id]['asset_id'] = item.Asset_num
            list_dict[item.id]['asset_name'] = item.Assert_name
            list_dict[item.id]['asset_key'] = item.Asset_key
            list_dict[item.id]['asset_user'] = item.Asset_user
            list_dict[item.id]['asset_status'] = ASSET_STATUS[str(item.Asset_status - 1)]
            list_dict[item.id]['asset_registertime'] = item.Asset_registertime.strftime('%Y-%m-%d %H:%M:%S')
            asset_list.append(list_dict[item.id])

        return {'total': counts, 'rows': asset_list}


def asset_scan_auto(ip_address, action, userid):
    db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
    if len(ip_address) == 0:
        dict_model['success'] = 0
        dict_model['result'] = '未选择符合要求的资产'
    if action == 'port':
        asset_port.delay(userid, ip_address.split(','))
        dict_model['success'] = 1
        dict_model['result'] = '任务已提交'
    elif action == 'segment':
        if len(ip_address.split('/')) > 1:
            asset_descover.delay(userid, ip_address)
            dict_model['success'] = 1
            dict_model['result'] = '任务已提交'
        else:
            dict_model['success'] = 0
            dict_model['result'] = '请填写正确的IP地址段'
    else:
        dict_model['success'] = 0
        dict_model['result'] = '请填写参数!'

    return dict_model


class AssetForRd(object):

    def __init__(self, asset_id, user_id):
        self.id = asset_id
        self.user_id = user_id

    def asset_read(self):
        global data, data_detail, data_bugs, data_ports, data_files, data_osinfo
        data = {}
        data_detail = {}
        data_bugs = {}
        data_ports = {}
        data_files = {}
        data_osinfo = {}

        db.session.commit()  # 清除程序以及数据库层面带来的缓存问题

        model = AssetmanageAsset.query.filter(AssetmanageAsset.id == int(self.id)).first()

        if model:
            data_detail = {
                'asset_name': model.Assert_name,
                'asset_num': model.Asset_num,
                'asset_registertime': model.Asset_registertime,
                'asset_ip': model.Asset_key,
                'asset_user': model.Asset_user,
                'asset_status': ASSET_STATUS[str(model.Asset_status - 1)],
                'asset_haver': model.Asset_score if model.Asset_score is not None else ''
            }
            model_bugs = VulnmanageScanvuln.query.filter_by(Vuln_asset_id=int(self.id)).filter(
                VulnmanageScanvuln.Leave != '0').all()
            if model_bugs:
                for p in model_bugs:
                    data_bugs[p.id] = {}
                    data_bugs[p.id]['Vuln_id'] = p.Vuln_id
                    data_bugs[p.id]['Vuln_name'] = p.Vuln_name
                    data_bugs[p.id]['Cve_name'] = p.Cve_name if p.Cve_name is not None else ''
                    data_bugs[p.id]['Leave'] = LEVEL_FOR_VULN[p.Leave]
                    data_bugs[p.id]['Create_data'] = p.Create_data

            model_ports = AssetmanageAssetPort.query.filter_by(Asset_id=int(self.id)).all()
            if model_ports:
                for k in model_ports:
                    data_ports[k.id] = {}
                    data_ports[k.id]['Port'] = k.Port
                    data_ports[k.id]['Requestname'] = k.Requestname
                    data_ports[k.id]['Product'] = k.Product
                    data_ports[k.id]['Version'] = k.Version
                    data_ports[k.id]['Port_info'] = k.Port_info
                    # data_ports[k.id]['Updatetime'] = k.Updatetime.strftime('%Y-%m-%d')
                    data_ports[k.id]['Updatetime'] = k.Updatetime
            model_osinfo = AssetmanageAssetO.query.filter_by(Asset_id=int(self.id)).first()
            if model_osinfo:
                data_osinfo = {
                    'Hostname': model_osinfo.Hostname,
                    'Osname': model_osinfo.Osname,
                    'CPU_model': model_osinfo.CPU_model,
                    'CPU_num': model_osinfo.CPU_num,
                    'Memory': model_osinfo.Memory,
                    'Disk': model_osinfo.Disk,
                    'Productor': model_osinfo.Productor,
                    'Up_time': model_osinfo.Up_time,
                    'Down_time': model_osinfo.Down_time,
                    'Guarante_time': model_osinfo.Guarante_time,
                    'Updatetime': model_osinfo.Updatetime
                }
            model_files = AssetmanageAssetFile.query.filter_by(Asset_id=int(self.id)).all()
            if model_files:
                for n in model_files:
                    data_files[n.id] = {
                        'Name': n.Name,
                        'Fileurl': n.Fileurl,
                        'Fileinfo': n.Fileinfo,
                        'Updatetime': n.Updatetime
                    }

            data = {
                'detail': data_detail,
                'osinfo': data_osinfo,
                'bugs': data_bugs,
                'ports': data_ports,
                'files': data_files
            }

        return data

    def asset_delete(self):
        pass
