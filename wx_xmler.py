#!/usr/bin/env python
# -*- coding: utf8
# 
# 
import logging
import re

logging.basicConfig(level=logging.DEBUG, format='(%(funcName)-10s) %(message)s')

class xmler(object):
    easy_restr = re.compile(r'\<(\w+)\>\<?(.*?)\>?\<\/')
    cdata_restr = re.compile(r'.*\[([\w\s]*)\]')
    key_restr = re.compile(r'\<(\w+)\>')

    def __init__(self, xmlstr, html=False):
        if xmlstr.startswith('<xml>'):
            xmlstr = xmlstr[5:-6]
        self.results = {}
        if html:
            self.xmlstr = escape(xmlstr)
        else:
            self.xmlstr = xmlstr

    @property
    def keys(self):
        return self.__class__.key_restr.findall(self.xmlstr, re.M)

    @property
    def dict(self, full=False):
        f1 = self.__class__.easy_restr
        f2 = self.__class__.cdata_restr
        rt = dict(f1.findall(self.xmlstr, re.M))
        for k,v in rt.items():
            if v.startswith('!'):
                rt[k] = f2.match(v).group(1)
        self.results.update(rt)
        return rt

    @property
    def xml(self):
        return '<xml>%s</xml>' % self.xmlstr

    def __getitem__(self, tag):
        tag = tag[1:] if tag.startswith('!') else tag
        if tag in self.results:
            return self.results[tag]
        findstr = r'\<' + tag + '\>\<?(.*?)\>?\<\/'
        rp = re.search(findstr, self.xmlstr, re.M)
        if rp:
            rt = rp.group(1)
            rt = rt[8:-2] if rt.startswith('!') else rt
            self.results[tag] = rt
        else:
            rt = ''
        return int(rt) if rt.isdigit() else rt

    def rep_val(self, findvar, repval):
        #   change a value
        repval = repval.decode('gbk')
        self.xmlstr = repval.join(re.split(findvar, self.xmlstr))
        return self.xmlstr

    def rep_val_bytag(self, findtag, val):
        #   set a value by tag
        findstr = r'(.*\<' + findtag + '\>).*?(\</.*)'
        self.xmlstr = val.join(re.split(findstr, self.xmlstr, re.M)[1:-1])
        return self.xmlstr


class wx_basedata(xmler):
    require_keys = None

    def __inner_check(self):
        xmlkeys = self.keys()
        try:
            [xmlkeys.remove(v[1:] if v.startswith('!') else v) for v in self.__class__.require_keys]
        except ValueError:
            return False
        return True if len(xmlkeys) == 0 else False

    def rep_val_bytag(self, findtag, val):
        val = val.decode('gbk') if isinstance(val, str) else val
        D = -1
        for tag in self.__class__.require_keys:
            D = tag.index(findtag)
            if D >= 0:
                break
        if D < 0:
            raise KeyError('not a leggle tag!')
        rt = re.split(r'(.*\<' + findtag + '\>).*?(\</.*)', self.xmlstr)[1:-1]
        if D == 1:
            #   no '!' at before
            val = '<![CDATA[%s]]>' % val
        return val.join(rt)

    def showmsg(self):
        raise NotImplementedError