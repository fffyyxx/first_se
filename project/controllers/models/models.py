# coding: utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import config
from werkzeug.security import check_password_hash, generate_password_hash

config_pro = config.ConfigDB

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config_pro.DB_HOST
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_pro.DB_EDIT

db = SQLAlchemy(app)


class AssetmanageAsset(db.Model):
    __tablename__ = 'assetmanage_asset'

    id = db.Column(db.INTEGER, primary_key=True)
    Asset_num = db.Column(db.String(50))
    Assert_name = db.Column(db.String(100), nullable=False)
    Asset_key = db.Column(db.String(50), nullable=False)
    Asset_user = db.Column(db.String(50))
    Asset_status = db.Column(db.INTEGER, nullable=False)
    Asset_registertime = db.Column(db.DateTime)
    Asset_updatetime = db.Column(db.DateTime)
    Asset_type = db.Column(db.String(45))
    Asset_score = db.Column(db.String(45))


class Menu(db.Model):
    __tablename__ = 'menu'

    id = db.Column(db.INTEGER, primary_key=True)
    Menu_Name = db.Column(db.String(50))
    Parent_id = db.Column(db.INTEGER)
    Url = db.Column(db.String(200))
    Index = db.Column(db.INTEGER, nullable=False)


class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.INTEGER, primary_key=True)
    per_name = db.Column(db.String(50))

    menus = db.relationship('Menu', secondary='role_menu_permission',
                            backref=db.backref('permissions', lazy='dynamic'), lazy='dynamic')


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.INTEGER, primary_key=True)
    RoleName = db.Column(db.String(50))

    permissions = db.relationship('Permission', secondary='role_menu_permission',
                                  backref=db.backref('roles', lazy='dynamic'), lazy='dynamic')


class TaskmanageScanner(db.Model):
    __tablename__ = 'taskmanage_scanner'

    id = db.Column(db.INTEGER, primary_key=True)
    Scannername = db.Column(db.String(50))
    Scannertype = db.Column(db.String(50))
    Scannerurl = db.Column(db.String(100))
    Scannerstatus = db.Column(db.String(50))
    Scannerapikey = db.Column(db.String(100))
    Scannerapisec = db.Column(db.String(100))
    Scannerdescription = db.Column(db.Text)
    Scanneraddtime = db.Column(db.DateTime)
    Scannerupdatetime = db.Column(db.DateTime)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.INTEGER, primary_key=True)
    UserName = db.Column(db.String(20))
    LoginName = db.Column(db.String(50))
    IsAdmin = db.Column(db.INTEGER)
    password_hash = db.Column(db.String(50))

    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    # def __init__(self, *args, **kwargs):
    #     self.LoginName = kwargs.get('Loginname')
    #     self.password_hash = generate_password_hash(kwargs.get('password_hash'))

    # 不可读取
    @property
    def password(self):
        raise AttributeError("you can not read it")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def confirm_password(self, password):
        return check_password_hash(self.password_hash, password)


class VulnmanageVulnerability(db.Model):
    __tablename__ = 'vulnmanage_vulnerability'

    id = db.Column(db.INTEGER, primary_key=True)
    Cve_id = db.Column(db.String(50))
    Cnvd_id = db.Column(db.String(50))
    Cve_name = db.Column(db.String(255))
    Leave = db.Column(db.String(10))
    Introduce = db.Column(db.Text)
    Scopen = db.Column(db.Text)
    Fix = db.Column(db.Text)
    Updatetime = db.Column(db.DateTime)


class AssetmanageAssetFile(db.Model):
    __tablename__ = 'assetmanage_asset_file'

    id = db.Column(db.INTEGER, primary_key=True)
    Name = db.Column(db.String(50))
    Fileurl = db.Column(db.String(255))
    Fileinfo = db.Column(db.Text)
    Updatetime = db.Column(db.DateTime)
    Asset_id = db.Column(db.ForeignKey('assetmanage_asset.id'), nullable=False, index=True)

    Asset = db.relationship('AssetmanageAsset')


class AssetmanageAssetO(db.Model):
    __tablename__ = 'assetmanage_asset_os'

    id = db.Column(db.INTEGER, primary_key=True)
    Hostname = db.Column(db.String(50))
    Osname = db.Column(db.String(100))
    CPU_model = db.Column(db.String(100))
    CPU_num = db.Column(db.String(100))
    Memory = db.Column(db.String(50))
    Disk = db.Column(db.String(255))
    Productor = db.Column(db.String(100))
    Up_time = db.Column(db.DateTime)
    Down_time = db.Column(db.DateTime)
    Guarante_time = db.Column(db.DateTime)
    Updatetime = db.Column(db.DateTime)
    Asset_id = db.Column(db.ForeignKey('assetmanage_asset.id'), nullable=False, index=True)

    Asset = db.relationship('AssetmanageAsset')


class AssetmanageAssetPort(db.Model):
    __tablename__ = 'assetmanage_asset_port'

    id = db.Column(db.INTEGER, primary_key=True)
    Port = db.Column(db.String(50))
    Requestname = db.Column(db.String(50))
    Product = db.Column(db.String(100))
    Version = db.Column(db.String(50))
    Port_info = db.Column(db.Text)
    Updatetime = db.Column(db.DateTime)
    Asset_id = db.Column(db.ForeignKey('assetmanage_asset.id'), nullable=False, index=True)

    Asset = db.relationship('AssetmanageAsset')


class Noticemanage(db.Model):
    __tablename__ = 'noticemanage'

    id = db.Column(db.INTEGER, primary_key=True)
    notice_title = db.Column(db.String(30), nullable=False)
    notice_body = db.Column(db.Text, nullable=False)
    notice_status = db.Column(db.INTEGER, nullable=False)
    notice_url = db.Column(db.String(50))
    notice_type = db.Column(db.String(30), nullable=False)
    notice_time = db.Column(db.DATETIME(6), nullable=False)
    notice_user_id = db.Column(db.INTEGER, nullable=False, index=True)


class RoleMenuPermission(db.Model):
    __tablename__ = 'role_menu_permission'

    id = db.Column(db.INTEGER, primary_key=True)
    # Role_id = db.Column(db.INTEGER, nullable=False)
    # Menu_id = db.Column(db.INTEGER, nullable=False)
    # Permission_id = db.Column(db.INTEGER, nullable=False, index=True)
    Role_id = db.Column(db.INTEGER, db.ForeignKey('role.id'))
    Menu_id = db.Column(db.INTEGER, db.ForeignKey('menu.id'))
    Permission_id = db.Column(db.INTEGER, db.ForeignKey('permission.id'))


class TaskmanageScannerpolicy(db.Model):
    __tablename__ = 'taskmanage_scannerpolicies'

    id = db.Column(db.INTEGER, primary_key=True)
    Policiesname = db.Column(db.String(50))
    Scanner_id = db.Column(db.ForeignKey('taskmanage_scanner.id'), nullable=False, index=True)
    Policies_key = db.Column(db.String(100))
    Policies_sec = db.Column(db.String(100))

    Scanner = db.relationship('TaskmanageScanner')


class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.INTEGER, primary_key=True)
    # User_id = db.Column(db.INTEGER, nullable=False)
    # Role_id = db.Column(db.INTEGER, nullable=False)
    User_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    Role_id = db.Column(db.INTEGER, db.ForeignKey('role.id'))


class VulnmanageScanvuln(db.Model):
    __tablename__ = 'vulnmanage_scanvuln'

    id = db.Column(db.INTEGER, primary_key=True)
    Vuln_id = db.Column(db.String(50))
    Vuln_name = db.Column(db.String(255))
    Cve_name = db.Column(db.String(50))
    Vuln_type = db.Column(db.String(60))
    Leave = db.Column(db.String(10))
    Introduce = db.Column(db.Text)
    Vuln_info = db.Column(db.Text)
    Scopen = db.Column(db.Text)
    Create_data = db.Column(db.DateTime)
    Update_data = db.Column(db.DateTime)
    Vuln_asset_id = db.Column(db.ForeignKey('assetmanage_asset.id'), nullable=False, index=True)

    Asset = db.relationship('AssetmanageAsset')


class VulnmanageVulnAdvance(db.Model):
    __tablename__ = 'vulnmanage_vuln_advance'

    id = db.Column(db.INTEGER, primary_key=True)
    Type = db.Column(db.String(50), nullable=False)
    Vuln_name = db.Column(db.String(255), nullable=False)
    Leave = db.Column(db.String(10), nullable=False)
    Fix = db.Column(db.String(8000), nullable=False, default=None)
    Create_data = db.Column(db.DATETIME(6), nullable=False)
    Update_data = db.Column(db.DATETIME(6), nullable=False)


class TaskmanageTask(db.Model):
    __tablename__ = 'taskmanage_task'

    id = db.Column(db.INTEGER, primary_key=True)
    Task_id = db.Column(db.String(50))
    Scan_id = db.Column(db.String(20))
    Taskname = db.Column(db.String(45))
    Tasktype = db.Column(db.String(45))
    Tasktarget = db.Column(db.String(45))
    Tasktargetinfo = db.Column(db.Text)
    Taskstatus = db.Column(db.String(20))
    Requeststatus = db.Column(db.String(20))
    Audittime = db.Column(db.DateTime)
    Auditinfo = db.Column(db.Text)
    Createtime = db.Column(db.DateTime)
    Audituserid = db.Column(db.ForeignKey('user.id'), nullable=False, index=True)
    Taskuserid = db.Column(db.ForeignKey('user.id'), nullable=False, index=True)
    Taskscannerid = db.Column(db.ForeignKey('taskmanage_scanner.id'), nullable=False, index=True)
    Scannerpoliceid = db.Column(db.ForeignKey('taskmanage_scannerpolicies.id'), nullable=False, index=True)

    user = db.relationship('User', primaryjoin='TaskmanageTask.Audituserid == User.id')
    taskmanage_scannerpolicy = db.relationship('TaskmanageScannerpolicy')
    taskmanage_scanner = db.relationship('TaskmanageScanner')
    user1 = db.relationship('User', primaryjoin='TaskmanageTask.Taskuserid == User.id')


class LoopholeVuln(db.Model):
    __tablename__ = 'loophole_vuln'

    id = db.Column(db.INTEGER, primary_key=True)
    url = db.Column(db.String(100))
    CNNVD = db.Column(db.String(20))
    title = db.Column(db.String(100))
    CVE = db.Column(db.String(20))
    grade = db.Column(db.String(20))
    loophole_type = db.Column(db.String(20))
    threat_type = db.Column(db.String(20))
    release_time = db.Column(db.String(20))
    update_time = db.Column(db.String(20))
    loophole_info = db.Column(db.String(800))
    loophole_bulletin = db.Column(db.String(250))
    reference_website = db.Column(db.String(250))
