from flask import Blueprint, render_template, request, json, session, redirect, url_for
from controllers.views.login import login_check
from ..users.userDAL import UserForAll, UserForRd
from controllers.models import models
from werkzeug.security import check_password_hash, generate_password_hash
from controllers.views.roles.roleDAL import RoleForRd

User = Blueprint('user', __name__, template_folder='templates', static_folder='static')


@User.route('/view/users')
@login_check
def view_users():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'users':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('users/userlist.html')


@User.route('/view/users_table', methods=['POST'])
def view_user_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = UserForAll(**dict_a).user_table()
            json_list = json.dumps(table_list)

# test
#             model = models.User.query.filter_by(UserName='ff').first()
#             ss = model.roles.all()
#             for s_r in ss:
#                 print(s_r.RoleName)
#             print('*'*10)
#             model1 = models.Role.query.filter_by(id=3).first()
#             s_u = model1.users
#             s = model1.permissions
#             print(s)
#             print('*' * 10)
#             model2 = models.Permission.query.filter_by(id=5).first()
#             s1 = model2.menus.all()[0].Menu_Name
#             s2 = model2.menus.all()[0]
#             print(s1)
#             print(s2)

            return json_list
        else:
            return json.dumps('')
    except Exception as e:
        print(e)


@User.route('/view/user_curd/<int:id>', methods=['DELETE', 'POST', 'GET'])
@login_check
def view_user_rd(id):
    try:
        if request.method == 'DELETE':
            data = UserForRd(id).user_delete()
            if data == '200':
                return json.dumps(dict(Success=1, Result='删除成功！'))
            else:
                return json.dumps(dict(Success=0, Result='删除失败,信息不存在！'))

        elif request.method == 'POST':
            data = UserForRd(id).user_edit()
            if data == '200':
                return json.dumps(dict(Success=1, Result='修改成功'))
            else:
                return json.dumps(dict(Success=0, Result='修改失败,信息不存在！'))

        elif request.method == 'GET':
            data = UserForRd(id).user_read()
            role_datalist = models.Role.query.filter(id > 0).all()
            role_listlen = len(role_datalist)
            return render_template('users/useredit.html', data=data, role_datalist=role_datalist,
                                   role_listlen=role_listlen)

    except Exception as e:
        print(e)


@User.route('/view/user_curd', methods=['POST', 'GET'])  # 新增、更新
@login_check
def view_user_cu():
    try:
        if request.method == 'GET':
            data_id = request.args.get('id') if request.args.get('id') is not None else 0
            data = UserForRd(data_id).user_read()
            role_datalist = models.Role.query.filter(models.Role.id > 0).all()
            return render_template('users/useredit.html', data=data, role_datalist=role_datalist)
            # return render_template('users/useredit1.html')
        elif request.method == 'POST':
            # 添加用户
            username_id = request.form.get('user_name')
            loginname_id = request.form.get('login_name')
            password = request.form.get('pd_hash')
            password_hash = generate_password_hash(password)
            user = models.User(UserName=username_id, LoginName=loginname_id, password_hash=password_hash)
            models.db.session.add(user)
            # 添加用户角色关联
            models.db.session.flush()
            userrole_uid = user.id
            # userrole_rid = request.form.get('role_name')
            userrole_rids = request.values.getlist('role_name')
            for userrole_rid in userrole_rids:
                userrole = models.UserRole(User_id=userrole_uid, Role_id=userrole_rid)
                models.db.session.add(userrole)

            models.db.session.commit()
            return json.dumps(dict(Success=1, Result='修改成功'))

        #     a = request.form
        #     json_a = json.dumps(a)
        #     dict_a = json.loads(json_a)
        #     info_now = TaskForCu(session['user_id'], **dict_a).task_create_or_update()
        #     return json.dumps(info_now)
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)