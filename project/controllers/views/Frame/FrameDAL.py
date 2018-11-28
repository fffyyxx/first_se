# coding:utf-8
from controllers.models.models import User, Menu, Role, UserRole, RoleMenuPermission, db
from sqlalchemy import or_


def viewmenu(username):
    db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
    model = User.query.filter_by(LoginName=username).first()
    global menu_list, menu_all, menu_dict
    menu_list = []
    menu_all = []
    menu_dict = {}
    try:
        if model.IsAdmin == 1:
            menu_all = Menu.query.filter(Menu.id).order_by(
                Menu.Index.asc()).all()  # 可以全部查出,但需要前端自行组合,渲染耗费时间

        else:
            menu_ids = Menu.query.join(RoleMenuPermission, RoleMenuPermission.Menu_id == Menu.id). \
                join(Role, Role.id == RoleMenuPermission.Role_id). \
                join(UserRole, UserRole.Role_id == Role.id). \
                join(User, User.id == UserRole.User_id).filter(User.id == model.id).all()  # 斜杠代表换行,回车后自动生成

            menu_all = Menu.query.filter(Menu.id.in_(menu_ids.id)).filter(Menu.Menu_Name != '系统管理',
                                                                          or_(Menu.Parent_id != 3,
                                                                              Menu.Parent_id == None)).order_by(
                Menu.Index.asc()).all()

        # else:
        #     menu_all = Menu.query.filter(Menu.Menu_Name != '系统管理',
        #                                  or_(Menu.Parent_id != 3,
        #                                      Menu.Parent_id == None)).order_by(
        #         Menu.Index.asc()).all()  # 可以全部查出,但需要前端自行组合,渲染耗费时间

        for item in menu_all:
            menu_dict[item.id] = {'index': 0, 'title': '', 'url': '', 'parent_id': 0, 'child': '', 'status': 0,
                                  'model': ''}
            menu_dict[item.id]['index'] = item.Index
            menu_dict[item.id]['title'] = item.Menu_Name
            menu_dict[item.id]['url'] = item.Url
            menu_dict[item.id]['parent_id'] = item.Parent_id
            menu_dict[item.id]['child'] = []
            menu_dict[item.id]['status'] = 0
            menu_dict[item.id]['model'] = str(item.Url).split('/')[-1]
        for i in menu_dict:
            if menu_dict[i]['parent_id']:
                pid = menu_dict[i]['parent_id']
                parent_menu = menu_dict[pid]
                parent_menu['child'].append(menu_dict[i])
            else:
                menu_list.append(menu_dict[i])

    except Exception as e:
        print(e)

    return menu_list


def viewusername(username):
    db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
    model = User.query.filter_by(LoginName=username).first()
    if model.UserName:
        return model.UserName
    else:
        return ''
