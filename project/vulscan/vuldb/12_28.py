# coding:utf-8
import paramiko
paramiko.util.logging.getLogger('paramiko.transport').addHandler(paramiko.util.logging.NullHandler())


def get_plugin_info():
    plugin_info = {
        "name": "SSH弱口令test",
        "info": "直接导致服务器被入侵控制。",
        "level": "紧急",
        "type": "弱口令",
        "author": "wolf@YSRC",
        "url": "",
        "keyword": "server:ssh",
        "source": 1
    }
    return plugin_info


def check(ip, port, timeout):
    user_list = ['admin', 'root', 'oracle', 'weblogic']
    PASSWORD_DIC = ['123456', 'admin', 'root', 'password', '123123', '123', '1', '{user}', '{user}{user}', '{user}@123',
                    '{user}123', '{user}2016', '{user}2015', '{user}!', '', 'P@ssw0rd!!', 'qwa123', '12345678', 'test',
                    'Admin@123', '123456789', '123321', '1314520', '666666', 'woaini', '000000',
                    '1234567890', '8888888', 'qwerty', '1qaz2wsx', 'abc123', 'abc123456', '1q2w3e4r', '123qwe',
                    '159357', 'p@ssw0rd', 'p@55w0rd', 'password!', 'p@ssw0rd!', 'password1', 'r00t', 'tomcat', 'apache',
                    'system', 'huawei', 'zte']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for user in user_list:
        for pass_ in PASSWORD_DIC:
            pass_ = str(pass_.replace('{user}', user))
            try:
                ssh.connect(ip, port, user, pass_, timeout=timeout, allow_agent = False, look_for_keys = False)
                ssh.exec_command('whoami',timeout=timeout)
                if pass_ == '': pass_ = "null"
                return u"%s存在弱口令，账号：%s，密码：%s" % (ip,user, pass_)
            except Exception as e:
                if "Authentication failed" == e:
                    return
                # print(e)
            finally:
                ssh.close()


# if __name__ == '__main__':
#     ip = '192.168.3.77'
#     port = 22
#     timeout = 10
#     print(check(ip,port,timeout))

