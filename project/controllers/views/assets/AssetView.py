# coding:utf-8
from flask import Blueprint, render_template, request, json, session
from controllers.views.login import login_check
from ..assets.AssetDAL import AssetForAll, asset_scan_auto, AssetForRd, AssetmanageAsset

Asset = Blueprint('asset', __name__, template_folder='templates', static_folder='static')

ASSET_STATUS = {
    '0': '运行状态',
    '1': '使用中',
    '2': '闲置中',
    '3': '已销毁',
}


@Asset.route('/view/asset')
@login_check
def view_asset():
    menu_list = session['treelist']
    for item in menu_list:
        item['status'] = 0
        for childinfo in item['child']:
            childinfo['status'] = 0
            if childinfo['model'] == 'asset':
                item['status'] = 1
                childinfo['status'] = 1
    session['treelist'] = menu_list
    return render_template('Asset/assetlist.html', data=ASSET_STATUS)


@Asset.route('/view/asset_table', methods=['POST'])
def view_tasks_table():
    try:
        if request.method == 'POST':
            a = request.form
            json_a = json.dumps(a)
            dict_a = json.loads(json_a)
            table_list = AssetForAll(**dict_a).asset_table()
            json_list = json.dumps(table_list)
            return json_list
        else:
            return json.dumps('')
    except Exception as e:
        print(e)


@Asset.route('/view/asset-scan', methods=['GET', 'POST'])
@login_check
def asset_scan():
    try:
        if request.method == 'GET':
            data_1 = AssetmanageAsset.query.group_by(AssetmanageAsset.Asset_key).all()
            data_2 = request.args.get('action') if request.args.get('action') is not None else ''
            return render_template('Asset/assetscan.html', data1=data_1, data2=data_2)
        else:
            a = request.form['ip_address'] if request.form['ip_address'] is not None else ''
            b = request.form['action'] if request.form['action'] is not None else ''
            info_now = asset_scan_auto(a, b, session['user_id'])
            return json.dumps(info_now)
    except Exception as e:
        print(e)


@Asset.route('/view/asset_curd/<int:id>', methods=['GET', 'POST'])
@login_check
def view_asset_rd(id):
    try:
        if request.method == 'GET':
            data = AssetForRd(id, session['user_id']).asset_read()
            return render_template('Asset/assetdetail.html', data=data)
        elif request.method == 'DELETE':
            data = AssetForRd(id, session['user_id']).asset_delete()
            if data == '200':
                return json.dumps(dict(Success=1, Result='删除成功！'))
            else:
                return json.dumps(dict(Success=0, Result='删除失败,信息不存在！'))
        else:
            return render_template('500.html'), 500
    except Exception as e:
        print(e)
