from flask import Blueprint, render_template, request, json, session, redirect, url_for
from controllers.views.login import login_check
from ..permissions.permissionDAL import PermissionForAll, PermissionForRd
from controllers.models import models

Permission = Blueprint('permission', __name__, template_folder='templates', static_folder='static')


@Permission.route('/view/permissions')
@login_check
def view_permissions():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'permissions':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('permission/permissionlist.html')


@Permission.route('/view/permissions_table', methods=['POST'])
def view_permission_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = PermissionForAll(**dict_a).permission_table()
            json_list = json.dumps(table_list)
            return json_list
        else:
            return json.dumps('')
    except Exception as e:
        print(e)


@Permission.route('/view/permission_curd/<int:id>', methods=['DELETE', 'GET', 'POST'])
@login_check
def view_permission_rd(id):
    try:
        if request.method == 'DELETE':
            data = PermissionForRd(id).permission_delete()
            if data == '200':
                return json.dumps(dict(Success=1, Result='删除成功！'))
            else:
                return json.dumps(dict(Success=0, Result='删除失败,信息不存在！'))

        elif request.method == 'POST':
            data = PermissionForRd(id).permission_edit()
            if data == '200':
                return json.dumps(dict(Success=1, Result='修改成功'))
            else:
                return json.dumps(dict(Success=0, Result='修改失败,信息不存在！'))

        elif request.method == 'GET':
            data = PermissionForRd(id).permission_read()
            return render_template('permission/permissionedit.html', data=data)

    except Exception as e:
        print(e)


@Permission.route('/view/permission_curd', methods=['POST', 'GET'])  # 新增、更新
@login_check
def view_permission_cu():
    try:
        if request.method == 'GET':
            data_id = request.args.get('id') if request.args.get('id') is not None else 0
            data = PermissionForRd(data_id).permission_read()
            return render_template('permission/permissionedit.html', data=data)
            # return render_template('users/useredit1.html')
        elif request.method == 'POST':
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
                rolepermission = models.RoleMenuPermission(
                                                           Permission_id=permissionmenu_pid,
                                                           Menu_id=permissionmenu_mid
                                                           )
                models.db.session.add(rolepermission)

            models.db.session.commit()
            return json.dumps(dict(Success=1, Result='修改成功'))
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)
