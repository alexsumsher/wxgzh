#!/usr/bin/env python
# -*- coding: utf8
# 
import time
from wx_consts import msg_common
from wx_xmler import wx_basedata
 
class wx_msg(wx_basedata):
    sender_keys = None
    def_reply = u'收到'

    def __init__(self, xmlstr='', ischeck=False, fromoid=''):
        if ischeck:
            assert self.__inner_check()
        # ini results to store __getitem___ value
        self.results = {}
        self.fromoid = fromoid
        # auto reply: check in do_filter, save reply
        self.reply = ''
        self.xmlstr = xmlstr
        if xmlstr.startswith('<xml>'):
            self.xmlstr = xmlstr[5:-6]
            if hasattr(self, 'do_filter'):
                #   when use msg to create message, it's no need to do filter
                self.do_filter()
        else:
            self.xmlstr = xmlstr
        

    def _make_msg(self, **kwvalues):
        #   at lest:
        if not self.__class__.sender_keys:
            raise ValueError('No keys!')
        data = dict.fromkeys(self.__class__.sender_keys)
        data.update(kwvalues)
        if ('FromUserName' not in data) or (not data['FromUserName']):
            data['FromUserName'] = msg_common['FromUserName']
        data['CreateTime'] = int(time.time())
        return self.outxml(data, self.__class__.sender_keys)


    @staticmethod
    def outxml(datas, keys, u=True, store=False):
        # outxml({'a':1,'b':'xyz','c':'ccc','d':'ddd','e':'eee'},('a','b', '<v', '!c','!d', '<v', '!e')) =>
        #   u'<xml><a>1</a><b>xyz</b><v><c><![CDATA[ccc]]></c><d><![CDATA[ddd]]></d></v><e><![CDATA[eee]]></e></xml>'
        packs = []
        xmlstr = u'<xml>%s</xml>' if u else '<xml>%s</xml>'
        inxml = ''
        for k in keys:
            if k[0] == '<':
                kn = k[1:]
                try:
                    packs.remove(kn)
                    inxml += '</%s>' % kn
                except ValueError:
                    packs.append(kn)
                    inxml += '<%s>' % kn
            elif k[0] == '!':
                kn = k[1:]
                inxml += '<%s><![CDATA[%s]]></%s>' % (kn, datas[kn], kn)
            else:
                inxml += '<{0}>{1}</{0}>'.format(k, datas[k])
        xmlstr = xmlstr % inxml
        if store:
            self.xmlstr = rtstr
        return xmlstr

    def replay(self):
        return self.def_reply


class wx_msg_text(wx_msg):
    require_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!Content', 'MsgId')
    sender_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!Content')

    def make_msg(self, content=None, **kwvalues):
        #   at lest: content
        touser = kwvalues.get('ToUserName') or self['FromUserName']
        if not touser:
            raise ValueError('no to user defined!')
        content = content if isinstance(content, (str, unicode)) else kwvalues['Content']
        if '<' in content:
            content = escape(content)
        data = {}
        data['ToUserName'] = touser
        data['FromUserName'] = kwvalues.get('FromUserName', msg_common['FromUserName'])
        data['CreateTime'] = int(time.time())
        data['MsgType'] = 'text'
        data['Content'] = content
        return self.outxml(data, self.__class__.sender_keys)

    def replay(self):
        return self['Content']


class wx_msg_picture(wx_msg):
    require_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!PicUrl', '!MediaId', 'MsgId')
    sender_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '<Image', '!MediaId', '<Image')

    def make_msg(self, **kwargs):
        print kwargs
        return self._make_msg(MsgType='image', **kwargs)


wxrmsg_mappings = {
    'text': wx_msg_text,
    'image': wx_msg_picture,
}