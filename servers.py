#!/usr/bin/env python
# -*- coding: utf8

"""
thingking:
1. the state keep the redirect page info
"""
from flask import Flask, request, send_from_directory, send_file, logging, redirect, url_for, session, abort
import json
import logging
import os
# import events for reg customize events function
import wx_events
from wx_gzh import gzh
from wx_runtime_users import rtuser

logging.basicConfig(level=logging.DEBUG, format='(%(funcName)-10s) %(message)s')

# 启动服务器
gzhsvr = gzh(appid='wxb2feb66da4987f82', secret='1e5e88ae7d42103f917a77b327b06708')

app = Flask(__name__)
app.secret_key  = os.environ.get('SECRET_KEY') or 'zxf***YFJEU7#@#1HFEiefj'
cur_folder = os.getcwd()


# 事件注册器，可针对特定的事件event key实现对应的处理内容，返回string(仅仅在内置的imcallback函数没有返回值时才会调用注册函数)
# 针对已经定义的事件:
# wxevent_mappings.values(): subscribe(不建议),wx_event_location,wx_event_CLICK,wx_event_VIEW 等
#   A test for reg func to event
#   by reg_func, set a function to handle some event identified by eventkey
#   reg_fun/unreg_fun...
#   if not set a imcallback method(self.reply==''), will find and call reg_functions to handle the event
def click_my_cus(event_data):
    rt = 'clicked on my cus'
    return rt

def when_subscribe(event_data):
    rt = 'subscribe!'
    return rt

wx_events.reg_func('wx_event_CLICK', 'show_my_follower', click_my_cus)
wx_events.reg_func('wx_event_subscribe', 'finally', when_subscribe)


# 后续增加智能对话接口，基于wx_msg_text，或者转发到客服系统，实现分发器
# part of wx_msg_text replier
wx_replier = None


# Views/Pages
"""
需要使用wx系统功能页面，使用eMixer: from libs.html_mixer import eMixer; 动态将wx js页面配置文件插入html
outfile = eMixer('applyforsceneid.html', 'parts', basedir=hfd, wxconfig=gzh.make_wxconfig(request.url, debug=False))
return send_file(outfile, mimetype='text/html')
eMixer(base_html_file, parts_of_html_files_folder_name_in_basedir, dir_path_holding_base_html_file, dynamic_segement_data_string)
in applyforsceneid.html:
<script src="http://res.wx.qq.com/open/js/jweixin-1.2.0.js"></script>
...<body>...</body>...
<script type="text/javascript">
{{Ssegment: wxconfig}}
...
</script>
"""
@app.route('/gzhusers', methods=['GET', 'POST'])
def gzhusers():
    if request.method == 'GET':
        page = request.args.get('subpage')
        if page == 'home':
            return '<html><body>HOME: %s </body></html>' % session['openid']
        elif page == 'empty home':
            return '<html><body>EMPTY HOME</body></html>'
        else:
            return '<html><body></body></html>'


# 预设的用户注册页面
@app.route('/gzh_auther', methods=['GET', 'POST'])
def auther():
    if request.method == 'GET':
        print request.args
        a_code = request.args.get('code')
        a_state = request.args.get('state')
        subpage = request.args.get('subpage')
        #   if refresh auth_page will no need to auth again(check session)
        pre_oid = session.get('openid')
        if pre_oid:
            return redirect(url_for('gzhusers', subpage=subpage))
        if a_code:
            rtu = rtuser.auth_user(code=a_code, appid=gzh.token['tokenid'], secret=gzh.token['tokense'])
            if rtu:
                return redirect(url_for('gzhusers', subpage=subpage))
            else:
                return redirect(url_for('gzhusers', subpage=subpage))
        else:
            #   when no code and no openid in session, goes from a direct url without a wx-redirect
            redirect_url = wxgzh.set_page_url(request.url)
            return u'<script language="javascript" type="text/javascript">window.location.assign("%s");</script>' % redirect_url
        return 'NOT LIGGLE!'
    print request.form


# 基础入口，和WX Server交互
@app.route('/wxgzh', methods = ['GET', 'POST'])
def wxgzh():
    if request.method == 'GET':
        if len(request.args) == 0:
            return 'nothing!'
        return gzhsvr.when_geted(request.args)
    #   when post user's text:
    #   POST /wxgzh?signature=fee500230e38f00143e18c2cffd9c92e366315fd&timestamp=1510654293&nonce=1176144732&openid=okUwT0h8M94dukXWhRrg1c80uboM
    print request.form
    fromoid = request.args.get('openid')
    usr_holder = dict(msger=None)
    rmode,msger = gzhsvr.when_posted(request.data, fromoid)
    if msger is None:
        return gzhsvr.rt_text(fromoid, 'unkown message!')
    if rmode == 'event' and if hasattr(msger, 'showmsg'):
        # by default, event returns by showmsg func;
        # if reg event func, which will be deal with reged func
        rp = msger.showmsg()
    elif rmode == 'text' and wx_replier:
        # text message is seperated, may work with some replier app
        cont = msger['Content']
        rp = wx_replier(cont, fromoid)
    else:
        # by default, msssage returns by reply func and u'收到' as default return
        rp = msger.reply()
    logging.info('reply to user with: %s', rp)
    if rp.startswith('<xml>'):
        return rp
    else:
        return gzhsvr.rt_text(fromoid, rp)


if __name__ == '__main__':
    print 'go...'
    app.debug = False
    app.run(host='0.0.0.0', port=80)