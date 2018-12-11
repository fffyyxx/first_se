from flask import Blueprint, render_template, request, json, session, redirect, url_for
from controllers.views.login import login_check
from ..roles.roleDAL import RoleForAll, RoleForRd
from controllers.models import models

Role = Blueprint('role', __name__, template_folder='templates', static_folder='static')


@Role.route('/view/roles')
@login_check
def view_roles():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'roles':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('roles/rolelist.html')


@Role.route('/view/roles_table', methods=['POST'])
def view_role_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = RoleForAll(**dict_a).role_table()
            json_list = json.dumps(table_list)
            return json_list
        else:
            return json.dumps('')
    except Exception as e:
        print(e)


@Role.route('/view/role_curd/<int:id>', methods=['DELETE', 'POST', 'GET'])
@login_check
def view_role_rd(id):
    try:
        if request.method == 'DELETE':
            data = RoleForRd(id).role_delete()
            if data == '200':
                return json.dumps(dict(Success=1, Result='删除成功！'))
            else:
                return json.dumps(dict(Success=0, Result='删除失败,信息不存在！'))

        elif request.method == 'POST':
            data = RoleForRd(id).role_edit()
            if data == '200':
                return json.dumps(dict(Success=1, Result='修改成功'))
            else:
                return json.dumps(dict(Success=0, Result='修改失败,信息不存在！'))

        elif request.method == 'GET':
            data = RoleForRd(id).role_read()
            return render_template('roles/roleedit.html', data=data)

    except Exception as e:
        print(e)


@Role.route('/view/role_curd', methods=['POST', 'GET'])  # 新增、更新
@login_check
def view_role_cu():
    try:
        if request.method == 'GET':
            data_id = request.args.get('id') if request.args.get('id') is not None else 0
            data = RoleForRd(data_id).role_read()
            return render_template('roles/roleedit.html', data=data)
            # return render_template('users/useredit1.html')
        elif request.method == 'POST':
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
            return json.dumps(dict(Success=1, Result='修改成功'))
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)
