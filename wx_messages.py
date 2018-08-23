#!/usr/bin/env python
# -*- coding: utf8
# 
import time
from wx_consts import msg_common
from wx_xmler import wx_basedata

#   ////////////////////////////////       PART OF MASSAGE         //////////////////////////////////   
#   ////////////////////////////////       PART OF MASSAGE         //////////////////////////////////   
class wx_msg(wx_basedata):
    sender_keys = None

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
        package = self.__class__.package if hasattr(self, 'package') else None
        return self.outxml(data, self.__class__.sender_keys, package=package)

    @staticmethod
    def outxml(datas, keys, u=True, store=False, package=None):
        #   cdatas: data with CDATA frame; datas:normal data, u->unicode(no need to encode to utf8)
        #   package: (pack_name, (inner_item_name1, inner_item_name2)), inner_item_name should be in keys and the same arrange
        #   eg: outxml({'a':1,'b':'xyz','c':'ccc','d':'ddd','e':'eee'},('a','b','!c','!d','!e'),package=('v',('!c','!d'))) =>
        #   u'<xml><a>1</a><b>xyz</b><v><c><![CDATA[ccc]]></c><d><![CDATA[ddd]]></d></v><e><![CDATA[eee]]></e></xml>'
        def mki(tag):
            ist = 0
            if tag.startswith('!'):
                tag = tag[1:]
                ist = 1
            v = datas[tag]
            # v = v if isinstance(v, unicode) else str(v).decode('utf8') # guess content from wx is utf8, need to decode to unicode to handle
            v = v if isinstance(v, unicode) else str(v)
            return u'<{tag}><![CDATA[{val}]]></{tag}>'.format(tag=tag, val=v) if ist else u'<{tag}>{val}</{tag}>'.format(tag=tag, val=v)

        conts = u''
        if package:
            packname,pkeys = package
            keys = list(keys)
            pid = keys.index(pkeys[0])
            pstr = u'<{0}>%s</{0}>'.format(packname)
            pconts = u''
            for k in pkeys:
                pconts += mki(k)
                keys.remove(k)
            pstr = pstr % pconts
        else:
            pid = len(keys) + 1
            pstr = u''
        i = 0
        for k in keys:
            if i == pid:
                conts += pstr
            conts += mki(k)
            i += 1
        #   when package the last one!
        if pid == i:
            conts += pstr
        rtstr =  '<xml>%s</xml>' % conts
        if store:
            self.xmlstr = rtstr
        return rtstr

    def replay(self):
        return u'收到'


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
    sender_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!MediaId')
    package = ('Image', ('!MediaId',))

    def make_msg(self, **kwargs):
        print kwargs
        return self._make_msg(MsgType='image', **kwargs)


wxrmsg_mappings = {
    'text': wx_msg_text,
    'image': wx_msg_picture,
}