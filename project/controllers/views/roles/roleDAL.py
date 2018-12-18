from controllers.models.models import User, db, Role, RoleMenuPermission
from sqlalchemy import or_
from flask import request
from controllers.models import models


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
        model1 = RoleMenuPermission.query.filter_by(Role_id=self.id).all()
        for m in model1:
            db.session.delete(m)
            db.session.commit()
        if model:
            db.session.delete(model)
            db.session.commit()
            return '200'
        else:
            return '404'

    def role_edit(self):
        db.session.commit()
        RoleForRd.role_delete(self)
        # 添加角色
        rolename_id = request.form.get('role_name')
        role = models.Role(RoleName=rolename_id)
        models.db.session.add(role)
        # 添加角色权限关联
        models.db.session.flush()
        rolepermission_rid = role.id
        # rolepermission_pid = request.form.get('permission_name')
        rolepermission_pids = request.values.getlist('permission_name')
        for rolepermission_pid in rolepermission_pids:
            model = models.RoleMenuPermission.query.filter_by(Permission_id=rolepermission_pid).all()
            for m in model:
                if m.Role_id == None:
                    menu_add = m.Menu_id
                    rolepermissionmenu = models.RoleMenuPermission(Role_id=rolepermission_rid,
                                                                   Permission_id=rolepermission_pid,
                                                                   Menu_id=menu_add)
                    models.db.session.add(rolepermissionmenu)
        models.db.session.commit()

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