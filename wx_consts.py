#!/usr/bin/env python
# -*- coding: utf8
# 中文菜单名不要用u''的方式写
svr_menu = {
    "button":[
    {
        'type': 'click',
        'name': '我的二维码',
        'key': 'qr_code_req'
    },
    {
        'name': '我的菜单',
        'sub_button': [
        {
            'type': 'view',
            'name':'在线广告',
            'url': 'http://www.xinzhouzhuan.com/fdsys/ttadv'
        },
        {
            'type': 'view',
            'name': '内置页面',
            'url': 'http://www.xinzhouzhuan.com/gzhusers'
        },
        {
            'type': 'view',
            'name': 'debug',
            'url': 'http://debugx5.qq.com'
        },
        {
            'type': 'click',
            'name': '我的客户',
            'key': 'show_my_follower'
        }
        ]
    },
    {
        'name': '测试页面',
        'sub_button': [
        {
            'type': 'view',
            'name': '成员申请',
            'url': 'http://www.xinzhouzhuan.com/gzh_auther?subpage=apply_for_qr'
        },
        {
            'type': 'view',
            'name': '我的客户',
            'url': 'http://www.xinzhouzhuan.com/gzh_auther?subpage=my_followers'
        },
        {
            'type': 'view',
            'name': '测试页面',
            'url': 'http://www.xinzhouzhuan.com/gzh_auther?subpage=home'
        }
        ]
    }
    ]
}

#   MODULE data structors
wxsmsg_mappings = {
    #   name: (path, keys,rtkeys)
    'get_token': ('/cgi-bin/token', ('grant_type', 'appid', 'secret'), ('access_token', 'expires_in')),
    'get_jticket': ('/cgi-bin/ticket/getticket', ('access_token', 'type'), ('errcode', 'errmsg', 'ticket', 'expires_in')),
    'post_create_menu': ('/cgi-bin/menu/create', ('access_token',), ('errcode', 'errmsg')),
    'get_subers': ('/cgi-bin/user/get', ('access_token', 'next_openid'), ('total', 'count', 'data', 'next_openid')),
    'show_suber': ('/cgi-bin/user/info', ('access_token', 'openid'), ('subscribe','openid','nickname','sex', 'language', 'city', 'province', 'country', 'headimgurl', 'subscribe_time', 'unionid', 'remark', 'groupid', 'tagid_list')),
    'get_page_token': ('/sns/oauth2/access_token', ('appid', 'secret', 'code', 'grant_type'), ('access_token', 'expires_in', 'refresh_token', 'openid', 'scope')),
    'refresh_page_token': ('/sns/oauth2/refresh_token', ('appid', 'grant_type', 'refresh_token'), ('access_token', 'expires_in', 'refresh_token', 'openid', 'scope')),
    #   a unsubcribe user info get with get_us_user_info; subscribed user info with show_suber(witch is ABOVE)
    'get_us_user_info': ('/sns/userinfo', ('access_token', 'openid', 'lang'), ('openid', 'nickname', 'sex', 'province', 'city', 'country', 'headimgurl', 'privilege')),
    'get_jsapi_ticket': ('/cgi-bin/ticket/getticket', ('access_token', 'type'), ('errcode', 'errmsg', 'ticket', 'expire_in')),
    'post_qr_tmp_ticket': ('/cgi-bin/qrcode/create', ('access_token',), ('ticket','expire_seconds','url')),
    'post_qr_ulimit_ticket': ('/cgi-bin/qrcode/create', ('access_token',), ('ticket','expire_seconds','url')),
    'get_qr_image': ('/cgi-bin/showqrcode', ('ticket',), 'FILE'),
    'get_system_tags': ('/cgi-bin/tags/get', ('access_token',), ('tags',))
}

wxsmsg_post_struct = {
    'post_qr_tmp_ticket': {'expire_seconds':604800, 'action_name': 'QR_SCENE', 'action_info': {'scene': {'scene_id': 0}}},
    #   we can make special post struct here!
    'post_qr_ulimit_ticket': {'action_name': 'QR_LIMIT_SCENE', 'action_info': {'scene': {'scene_id': 0}}},
    'post_qr_ulimit_ticket_1': {'action_name': 'QR_LIMIT_SCENE', 'action_info': {'scene': {'scene_id': 0}}}
}

msg_common = {
    'FromUserName': 'gh_724496f00735',
    'test_token': 'alexsum',
    'default_text_reply': u'收到信息，稍后回复',
    'def_success': 'success'
}

wx_CONSTS = {
    'action_name': ('QR_SCENE', 'QR_STR_SCENE', 'QR_LIMIT_SCENE', 'QR_LIMIT_STR_SCENE'),
    'lang': ('zh_CN', 'zh_TW', 'en')
}
