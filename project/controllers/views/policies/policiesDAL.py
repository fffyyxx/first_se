# coding:utf-8
from controllers.models.models import TaskmanageScannerpolicy, db


class PoliciesForAll(object):
    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']

    def policies_table(self):
        global counts, policy_dict, policy_list
        counts = 0
        policy_dict = {}
        policy_list = []

        page_num = int(self.offset) / int(self.limit) + 1
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        policy_data = TaskmanageScannerpolicy.query. \
            filter(
            TaskmanageScannerpolicy.Policiesname.like('%' + self.txt_keys + '%') if self.txt_keys is not None else ""
            ).order_by(TaskmanageScannerpolicy.id.desc())

        policy_items = policy_data.paginate(page_num, per_page=self.limit, error_out=False).items
        counts = policy_data.count()

        for item in policy_items:
            policy_dict[item.id] = {}
            policy_dict[item.id]['id'] = item.id
            policy_dict[item.id]['policyname'] = item.Policiesname
            policy_dict[item.id]['scannername'] = item.Scanner.Scannername
            policy_list.append(policy_dict[item.id])

        return {'total': counts, 'rows': policy_list}
