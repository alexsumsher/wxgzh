#!/usr/bin/env python
# -*- coding: utf8
from flask import session
from wx_gzh import wx_smsg
# a simple user holder at runtime, work with session

class rtuser(object):
    count = 0

    @classmethod
    def auth_user(cls, code, appid, secret, getuinfo=False):
        #   https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
        snsapi_mode = 'snsapi_userinfo' if getuinfo else 'snsapi_base'
        jrt = {}
        with wx_smsg('get_page_token', baseurl='api.weixin.qq.com', appid=appid, secret=secret, code=code, grant_type='authorization_code') as getter:
            jrt = getter.get()
        if 'errcode' in jrt:
            print jrt['errmsg']
            return None
        openid = jrt['openid']
        return rtuser(openid, authed='yes')

    def __init__(self, openid='', authed='no'):
        session['openid'] = openid
        session['authed'] = authed

    def subscribe(self):
        session['subed'] = 'yes'

    def unsubscribe(self):
        session['subed'] = 'no'


class mem_users(object):
    pass
