# -*- conding:utf8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# celery默认配置
CELERY_BROKER_URL = 'amqp://root:root@localhost'
CELERY_RESULT_BACKEND = 'amqp://root:root@localhost'
CELERY_TASK_PROTOCOL = 1
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

CELERY_IMPORTS = [
    'controllers.views.assets.functions.tasks',
    'controllers.views.task.functions.tasks'
]


class ConfigWeb(object):
    WEB_HOST = '0.0.0.0'
    WEB_PORT = 8806
    # WEB_USER = 'root','user'
    # WEB_PASSWORD = '123','321'


class ConfigDB(ConfigWeb):
    # DB_HOST = 'mysql+pymysql://root:vm123@192.168.5.12:3306/new_semf?charset=utf8'
    DB_HOST = 'mysql+pymysql://root:root@127.0.0.1:3306/new_semf?charset=utf8'
    DB_EDIT = True


# 设置缓存文件路径
TMP_PATH = os.path.join(BASE_DIR, 'tmp')
