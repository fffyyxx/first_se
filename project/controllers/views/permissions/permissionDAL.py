from controllers.models.models import User, db, Role, Permission, RoleMenuPermission
from sqlalchemy import or_
from flask import request
from controllers.models import models


class PermissionForAll(object):

    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']

    def permission_table(self):
        global counts, permission_dict, permission_list
        counts = 0
        permission_dict = {}
        permission_list = []

        page_num = int(self.offset) / int(self.limit) + 1
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        permission_data = Permission.query. \
            filter(or_(Permission.per_name.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '',
                       Permission.id.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '')). \
            order_by(Permission.id.desc())

        permission_items = permission_data.paginate(int(page_num), per_page=self.limit, error_out=False).items
        counts = permission_data.count()

        for item in permission_items:
            permission_dict[item.id] = {}
            permission_dict[item.id]['id'] = item.id
            permission_dict[item.id]['permission_name'] = item.per_name
            permission_list.append(permission_dict[item.id])

        return {'total': counts, 'rows': permission_list}


class PermissionForRd(object):

    def __init__(self, data_id):
        self.id = data_id

    def permission_delete(self):
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        model = Permission.query.filter_by(id=self.id).first()
        model1 = RoleMenuPermission.query.filter_by(Permission_id=self.id).all()
        for m in model1:
            db.session.delete(m)
            db.session.commit()
        if model:
            db.session.delete(model)
            db.session.commit()
            return '200'
        else:
            return '404'

    def permission_edit(self):
        db.session.commit()
        # model = Permission.query.filter_by(id=self.id).first()
        # if model:
        #     model.per_name = request.form.get('permission_name')
        #     db.session.commit()
        #     return '200'
        # else:
        #     return '404'

        PermissionForRd.permission_delete(self)
        # 添加权限
        pername = request.form.get('permission_name')
        permission = models.Permission(per_name=pername)
        models.db.session.add(permission)
        # 添加权限菜单关联
        models.db.session.flush()
        permissionmenu_pid = permission.id
        # permissionmenu_mid = request.form.get('menu_url')
        permissionmenu_mids = request.values.getlist('menu_url')
        for permissionmenu_mid in permissionmenu_mids:
            rolepermission = models.RoleMenuPermission(Permission_id=permissionmenu_pid,
                                                       Menu_id=permissionmenu_mid)
            models.db.session.add(rolepermission)

        models.db.session.commit()

    def permission_read(self):
        global data
        data = {}

        db.session.commit()

        model = Permission.query.filter_by(id=int(self.id)).first()
        if model:
            data = {
                'permission_name': model.per_name,

            }
        else:
            data = {
                'permission_name': '',

            }
        return data
