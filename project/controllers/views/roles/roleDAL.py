from controllers.models.models import User, db, Role
from sqlalchemy import or_
from flask import request


class RoleForAll(object):

    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']

    def role_table(self):
        global counts, role_dict, role_list
        counts = 0
        role_dict = {}
        role_list = []

        page_num = int(self.offset) / int(self.limit) + 1
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        role_data = Role.query. \
            filter(or_(Role.RoleName.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '',
                       Role.id.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '')). \
            order_by(Role.id.desc())

        role_items = role_data.paginate(int(page_num), per_page=self.limit, error_out=False).items
        counts = role_data.count()

        for item in role_items:
            role_dict[item.id] = {}
            role_dict[item.id]['id'] = item.id
            role_dict[item.id]['role_name'] = item.RoleName
            role_list.append(role_dict[item.id])

        return {'total': counts, 'rows': role_list}


class RoleForRd(object):

    def __init__(self, data_id):
        self.id = data_id

    def role_delete(self):
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        model = Role.query.filter_by(id=self.id).first()
        if model:
            db.session.delete(model)
            db.session.commit()
            return '200'
        else:
            return '404'

    def role_edit(self):
        db.session.commit()
        model = Role.query.filter_by(id=self.id).first()
        if model:
            model.RoleName = request.form.get('role_name')
            db.session.commit()
            return '200'
        else:
            return '404'

    def role_read(self):
        global data
        data = {}

        db.session.commit()

        model = Role.query.filter_by(id=int(self.id)).first()
        if model:
            data = {
                'role_name': model.RoleName,

            }
        else:
            data = {
                'role_name': '',

            }
        return data