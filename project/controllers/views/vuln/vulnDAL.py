# coding:utf-8
from controllers.models.models import AssetmanageAsset, VulnmanageVulnerability, VulnmanageScanvuln, LoopholeVuln, db
from controllers.models.libs.checkip import checkip
from sqlalchemy import or_

LEVEL_FOR_VULN = {
    '0': '常规',
    '1': '低危',
    '2': '中危',
    '3': '高危',
    '4': '紧急'
}

dict_model = dict(success=1, result='')


class VulnForAll(object):

    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']
        self.vuln_level = kwargs['vuln_level']

    def vuln_table(self):
        db.session.commit()  # 解决程序以及数据库层面带来的缓存问题
        global counts, vuln_list, list_dict, vuln_asset_id
        counts = 0
        vuln_list = []
        list_dict = {}
        vuln_asset_id = 0

        page_num = int(self.offset) / int(self.limit) + 1

        if checkip(self.txt_keys):
            model_asset = AssetmanageAsset.query.filter_by(Asset_key=self.txt_keys).first()
            if model_asset:
                vuln_asset_id = model_asset.id

        vuln_data = VulnmanageScanvuln.query.filter(
            or_(VulnmanageScanvuln.Vuln_asset_id == vuln_asset_id if vuln_asset_id != 0 else '',
                VulnmanageScanvuln.Vuln_name.like(
                    '%' + self.txt_keys + '%') if self.txt_keys is not None else '')).filter(
            VulnmanageScanvuln.Leave != '0').order_by(VulnmanageScanvuln.id.desc())

        if self.vuln_level != '-1':
            vuln_data = vuln_data.filter(VulnmanageScanvuln.Leave == self.vuln_level)

        vuln_items = vuln_data.paginate(int(page_num), per_page=self.limit, error_out=False).items

        counts = vuln_data.count()

        for item in vuln_items:
            list_dict[item.id] = {}
            list_dict[item.id]['id'] = item.id
            list_dict[item.id]['vuln_id'] = item.Vuln_id
            list_dict[item.id]['vuln_name'] = item.Vuln_name
            list_dict[item.id]['vuln_level'] = LEVEL_FOR_VULN[item.Leave]
            # list_dict[item.id]['vuln_type'] = item.Vuln_type
            list_dict[item.id]['create_data'] = item.Create_data.strftime('%Y-%m-%d %H:%M:%S')
            list_dict[item.id]['vuln_asset'] = item.Asset.Asset_key
            vuln_list.append(list_dict[item.id])

        return {'total': counts, 'rows': vuln_list}


# loophole的漏洞库界面数据库处理
class LoopholeForAll(object):
    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']

    def loophole_table(self):
        global counts, loophole_dict, loophole_list
        counts = 0
        loophole_dict = {}
        loophole_list = []

        page_num = int(self.offset) / int(self.limit) + 1
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        # 搜索设置
        loophole_data = LoopholeVuln.query. \
            filter(or_(LoopholeVuln.CVE.like('%' + self.txt_keys + '%') if self.txt_keys is not None else "",
                       LoopholeVuln.release_time.like('%' + self.txt_keys + '%') if self.txt_keys is not None else "")). \
            order_by(LoopholeVuln.id.desc())

        loophole_items = loophole_data.paginate(page_num, per_page=self.limit, error_out=False).items
        counts = loophole_data.count()

        for item in loophole_items:
            loophole_dict[item.id] = {}
            loophole_dict[item.id]['id'] = item.id
            loophole_dict[item.id]['url'] = item.url
            loophole_dict[item.id]['CNNVD'] = item.CNNVD
            loophole_dict[item.id]['title'] = item.title
            loophole_dict[item.id]['CVE'] = item.CVE
            loophole_dict[item.id]['grade'] = item.grade
            loophole_dict[item.id]['loophole_type'] = item.loophole_type
            loophole_dict[item.id]['threat_type'] = item.threat_type
            loophole_dict[item.id]['release_time'] = item.release_time
            loophole_dict[item.id]['update_time'] = item.update_time
            loophole_dict[item.id]['loophole_info'] = item.loophole_info
            loophole_dict[item.id]['loophole_bulletin'] = item.loophole_bulletin
            loophole_dict[item.id]['reference_website'] = item.reference_website
            loophole_list.append(loophole_dict[item.id])

        return {'total': counts, 'rows': loophole_list}


class LoopholeForRd(object):

    def __init__(self, data_id):
        self.id = data_id

    def loophole_read(self):
        model = LoopholeVuln.query.filter_by(id=int(self.id)).first()
        if model:
            data = {
                'id': model.id,
                'url': model.url,
                'CNNVD': model.CNNVD,
                'title': model.title,
                'CVE': model.CVE,
                'grade': model.grade,
                'loophole_type': model.loophole_type,
                'threat_type': model.threat_type,
                'release_time': model.release_time,
                'update_time': model.update_time,
                'loophole_info': model.loophole_info,
                'loophole_bulletin': model.loophole_bulletin,
                'reference_website': model.reference_website
            }
            return data
        else:
            return '404'

    def loophole_delete(self):
        model = LoopholeVuln.query.filter_by(id=self.id).first()
        if model:
            db.session.delete(model)
            db.session.commit()
            return '200'
        else:
            return '404'
