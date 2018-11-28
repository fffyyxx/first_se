$('.submit').click(function () {
    var name = $('#username').val()
    var pwd = $('#password').val()
    if(name == '') {
        layer.msg('用户名不能为空！', {icon:2, time: 2000, zIndex:999 });
        name.focus();
    }else if(pwd == ''){
        layer.msg('密码不能为空！', {icon:2, time: 2000, zIndex:999 });
        pwd.focus();
    }else {
        $('form').submit()
    }
});