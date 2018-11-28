# coding:utf-8
from controllers.models.models import TaskmanageScanner, db


class ScannersForAll(object):
    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']
        self.scanner_status = int(kwargs['status'])

    def scanners_table(self):
        global counts, scanner_dict, scanner_list
        counts = 0
        scanner_dict = {}
        scanner_list = []

        page_num = int(self.offset) / int(self.limit) + 1
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        scanner_data = TaskmanageScanner.query. \
            filter(TaskmanageScanner.Scannername.like('%' + self.txt_keys + '%') if self.txt_keys is not None else "",
                   TaskmanageScanner.Scannerstatus == self.scanner_status if self.scanner_status != 0 else ""
                   ).order_by(TaskmanageScanner.id.desc())

        scanner_items = scanner_data.paginate(page_num, per_page=self.limit, error_out=False).items
        counts = scanner_data.count()

        for item in scanner_items:
            scanner_dict[item.id] = {}
            scanner_dict[item.id]['id'] = item.id
            scanner_dict[item.id]['scannername'] = item.Scannername
            scanner_dict[item.id]['scannertype'] = item.Scannertype
            scanner_dict[item.id]['scannerurl'] = item.Scannerurl
            scanner_dict[item.id]['scannerstatus'] = item.Scannerstatus
            scanner_dict[item.id]['createtime'] = item.Scanneraddtime.strftime('%Y-%m-%d %H:%M:%S')
            scanner_list.append(scanner_dict[item.id])

        return {'total': counts, 'rows': scanner_list}
