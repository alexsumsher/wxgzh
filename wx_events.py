#!/usr/bin/env python
# -*- coding: utf8
# 
import time
from wx_consts import msg_common
from wx_xmler import wx_basedata

#   functions that reg/unreg function to wx_event_handle
def filter_func(ename, key):
    es = wxevent_reg_funcs.get(ename)
    key = key or 'finally'
    if es:
        return es.get(key)
    #   finally, try to get function with key: finally
    return None

def reg_func(ename, key, func):
    #   reg function to wxevents
    if not callable(func):
        print 'func to reg should be callable'
        return 0
    if ename in wxevent_reg_funcs:
        es = wxevent_reg_funcs[ename]
        if key in es:
            unreg_func(ename, key)
    else:
        wxevent_reg_funcs[ename] = {}
        es = wxevent_reg_funcs[ename]
    es[key] = func
    return 1

def unreg_func(ename, key):
    if key in wxevent_reg_funcs[ename]:
        wxevent_reg_funcs[ename].remove(key)
        return 1
    else:
        return 0

  
class wx_event(wx_basedata):
    #   event will not export xml, must take a xmlstr

    def __init__(self, xmlstr, ischeck=False, fromoid=''):
        if ischeck:
            assert self.__inner_check()
        self.results = {}
        if xmlstr.startswith('<xml>'):
            xmlstr = xmlstr[5:-6]
        self.xmlstr = xmlstr
        self.reply = ''
        #   imcallback: work for reply
        #   filter_func: work for record like
        if hasattr(self, 'imcallback'):
            self.imcallback()
        print 'event_key: %s' % self['EventKey']
        if not self.reply:
            solver = filter_func(self.__class__.__name__, self['EventKey'])
            if solver:
                print 'solver get with: %s' % solver.__name__
                try:
                    self.reply = solver(self.dict)
                except:
                    pass

    def imcallback(self):
        pass

    def showmsg(self):
        return msg_common['def_success']

#   subscribe/unsubscribe in one object!
class wx_event_subscribe(wx_event):
    require_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!Event')

    # def imcallback(self):
        # if self['Event'] == 'subscribe':
            # wx_users.wx_uinfo(self['!FromUserName'], '', con=mdl_cons, todb=todb, issubu=1, dbmode='insert')
            # sp_getters.subscribe_2db(self.dict)
            # self.reply = local_defaults['def_welcome_msg']
        # elif self['Event'] == 'unsubscribe':
            # mdl_cons.execute_db('UPDATE wx_infos SET subscribe=1 WHERE openid=%s' % self['!FromUserName'])
            # sp_getters.subscribe_2db(self.dict, mode=0)
            # self.reply = ''

    def showmsg(self):
        return self.reply

class wx_event_location(wx_event):
    require_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!Event', 'Latitude', 'Longitude', 'Precision')

    def imcallback(self):
        user = self['FromUserName']
        lat = self['Latitude']
        lng = self['Longitude']
        prs = self['Precision']
        print 'user: %s with location:%s x %s!' % (user, lat, lng)


class wx_event_CLICK(wx_event):
    require_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!Event', '!EventKey')

    def imcallback(self):
        fstr = self['EventKey']
        if fstr == 'sample':
            self.reply = 'done sample'
        elif fstr == 'testing':
            self.reply = 'done testing'
        else:
            self.reply = ''

    def showmsg(self):
        return self.reply or self['EventKey']


class wx_event_VIEW(wx_event):
    require_keys = ('!ToUserName', '!FromUserName', 'CreateTime', '!MsgType', '!Event', '!EventKey')

    def imcallback(self):
        print 'wx_event_VIEW:',self['EventKey']


wxevent_mappings = {
    'subscribe': wx_event_subscribe,
    'unsubscribe': wx_event_subscribe,
    'LOCATION': wx_event_location,
    'CLICK': wx_event_CLICK,
    'VIEW': wx_event_VIEW
}

wxevent_reg_funcs = {
    # fun_id: func(event_data)
    'wx_event_subscribe': {}
}