/*弹出层*/

/*
    参数解释：
    title   标题
    url     请求的url
    id      需要操作的数据id
    w       弹出层宽度（缺省调默认值）
    h       弹出层高度（缺省调默认值）
*/
function x_admin_show(title, url, w, h) {
    if (title == null || title == '') {
        title = false;
    }
    ;
    if (url == null || url == '') {
        url = "404.html";
    }
    ;
    if (w == null || w == '') {
        w = ($(window).width() * 0.9);
    }
    ;
    if (h == null || h == '') {
        h = ($(window).height() - 50);
    }
    ;
    layer.open({
        type: 2,
        area: [w, h],
        fix: false, //不固定
        maxmin: true,
        shadeClose: true,
        shade: 0.4,
        zIndex: 9999,
        title: title,
        content: url
    });
}

function x_admin_confirm(title, url, type) {
    layer.confirm('该操作具备一定的风险<br>点击确定后,不可恢复', {
        btn: ['确定', '取消'], //按钮
        icon: 7,
        title: title
    }, function () {
        $.ajax({
            url: url,
            cache: false,
            contentType: 'application/json',
            dataType: 'json',
            async: false,
            type: type,
            success: function (data) {
                if (data.Success == 1) {
                    $('#example2').bootstrapTable('refresh');
                    showSuccessMsg(data.Result);
                } else {
                    showErrorMsg(data.Result)
                }
            }
        });
    }, function () {
    });
}

/*关闭弹出框口*/
function x_admin_close() {
    var index = parent.layer.getFrameIndex(window.name);
    parent.layer.close(index);
}

//操作成功消息提示
function showSuccessMsg(msg) {
    layer.msg(msg, {icon: 1, time: 2000, zIndex: 200000000});
}

//操作错误消息提示
function showErrorMsg(msg) {
    if (msg == '登录超时,请刷新页面') {
        layer.msg(msg, {icon: 2, time: 2000, zIndex: 200000000}, function () {
            top.location.href = "/login";
        });
    } else {
        layer.msg(msg, {icon: 2, time: 4000, zIndex: 200000000});
    }

}

//操作提醒消息提示
function showPromptMsg(msg) {
    layer.msg(msg, {icon: 7, time: 2000, zIndex: 200000000});
}

//获取URL传递的参数
function GetQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
}

//修改——转换日期格式(时间戳转换为datetime格式)
function changeDateFormat(cellval) {
    if (cellval != null) {
        var date = new Date(parseInt(cellval.replace("/Date(", "").replace(")/", ""), 10));
        var month = date.getMonth() + 1 < 10 ? "0" + (date.getMonth() + 1) : date.getMonth() + 1;
        var currentDate = date.getDate() < 10 ? "0" + date.getDate() : date.getDate();
        var hour = date.getHours() < 10 ? "0" + date.getHours() : date.getHours();
        var min = date.getMinutes() < 10 ? "0" + date.getMinutes() : date.getMinutes();
        var sec = date.getSeconds() < 10 ? "0" + date.getSeconds() : date.getSeconds();
        return date.getFullYear() + "-" + month + "-" + currentDate + " " + hour + ":" + min + ":" + sec;
    }
}

function GMTDateFormat(celltime) {
    if (celltime != null) {
        var date = new Date(celltime);
        return (date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds());
    }
}

//调用方式
//convertTime(dt,"yyyy-MM-dd HH:mm:ss")

function convertTime(jsonTime, format) {
    try {
        if (jsonTime != "") {
            var date = new Date(parseInt(jsonTime.replace("/Date(", "").replace(")/", ""), 10));
            var formatDate = date.format(format);
            return formatDate;
        }
        else {
            return "";
        }
    }
    catch (ex) {
        return "";
    }
}

Date.prototype.format = function (format) {
    var date = {
        "M+": this.getMonth() + 1,
        "d+": this.getDate(),
        "h+": this.getHours(),
        "m+": this.getMinutes(),
        "s+": this.getSeconds(),
        "q+": Math.floor((this.getMonth() + 3) / 3),
        "S+": this.getMilliseconds()
    };

    if (/(y+)/i.test(format)) {
        format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
    }

    for (var k in date) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1 ? date[k] : ("00" + date[k]).substr(("" + date[k]).length));
        }
    }

    return format;
}

//设置cookie
function setCookie(name, value, hours) {
    var exp = new Date();
    exp.setTime(exp.getTime() + hours * 60 * 60 * 1000);
    //exp.setTime(exp.getTime() + hours * 60 * 1000);
    document.cookie = name + "=" + escape(value) + ";path=/;expires=" + exp.toGMTString();
}

//删除cookie
function delCookie(name) {
    var date = new Date();
    date.setTime(date.getTime() - 10000);
    document.cookie = name + "=a; expires=" + date.toGMTString();
}

//读取cookie
function getCookie(name) {
    var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
    if (arr = document.cookie.match(reg))
        return unescape(arr[2]);
    else
        return null;
}

function newGuid() {
    var guid = "";
    for (var i = 1; i <= 32; i++) {
        var n = Math.floor(Math.random() * 16.0).toString(16);
        guid += n;
        if ((i == 8) || (i == 12) || (i == 16) || (i == 20))
            guid += "-";
    }
    return guid;
}

//当前日期yyyy-MM-dd
function getNowFormatDate() {
    var date = new Date();
    var seperator1 = "-";
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate;
    return currentdate;
}

// $("body").slimScroll({
//     width: 'auto',
//     height: 'auto',
//     start: 'bottom', //默认滚动位置：top/bottom
//     borderRadius: '0px', //滚动条圆角
//     railBorderRadius: '0px',//轨道圆角
//     disableFadeOut: false, //是否 鼠标经过可滚动区域时显示组件，离开时隐藏组件
//     alwaysVisible: true //是否 始终显示组件
// });