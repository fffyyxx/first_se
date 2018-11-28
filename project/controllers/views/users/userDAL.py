from controllers.models.models import User, db, Role
from sqlalchemy import or_
from flask import request
from werkzeug.security import check_password_hash, generate_password_hash


class UserForAll(object):

    def __init__(self, **kwargs):
        self.limit = int(kwargs['limit'])
        self.offset = int(kwargs['offset'])
        self.txt_keys = kwargs['txt_keys']
        self.user_id = int(kwargs['user_id'])
        self.is_admin = int(kwargs['is_admin'])

    def user_table(self):
        global counts, user_dict, user_list
        counts = 0
        user_dict = {}
        user_list = []

        page_num = int(self.offset) / int(self.limit) + 1
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        user_data = User.query. \
            filter(or_(User.LoginName.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '',
                       User.UserName.like('%' + self.txt_keys + '%') if self.txt_keys is not None else '')). \
            order_by(User.id.desc())

        # if self.is_admin != 1:
        #     user_data = user_data.filter(User.Taskuserid == self.user_id)

        user_items = user_data.paginate(int(page_num), per_page=self.limit, error_out=False).items
        counts = user_data.count()

        for item in user_items:
            user_dict[item.id] = {}
            user_dict[item.id]['id'] = item.id
            user_dict[item.id]['user_name'] = item.UserName
            user_dict[item.id]['login_name'] = item.LoginName
            user_dict[item.id]['is_admin'] = item.IsAdmin
            user_dict[item.id]['pd_hash'] = item.password_hash
            user_list.append(user_dict[item.id])

        return {'total': counts, 'rows': user_list}


class UserForRd(object):

    def __init__(self, data_id):
        self.id = data_id

    def user_delete(self):
        db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
        model = User.query.filter_by(id=self.id).first()
        if model:
            db.session.delete(model)
            db.session.commit()
            return '200'
        else:
            return '404'

    def user_edit(self):
        db.session.commit()
        model = User.query.filter_by(id=self.id).first()
        if model:
            model.UserName = request.form.get('user_name')
            model.LoginName = request.form.get('login_name')
            password = request.form.get('pd_hash')
            password_hash = generate_password_hash(password)
            model.password_hash = password_hash
            db.session.commit()
            return '200'
        else:
            return '404'

    def user_read(self):
        global data
        data = {}

        db.session.commit()

        model = User.query.filter_by(id=int(self.id)).first()
        if model:
            data = {
                'user_name': model.UserName,
                'login_name': model.LoginName,
                'is_admin': model.IsAdmin,
                'pd_hash': ''
            }
        else:
            data = {
                'user_name': '',
                'login_name': '',
                'is_admin': '',
                'pd_hash': ''
            }
        return data
