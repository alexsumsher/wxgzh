#!/usr/bin/env python
# -*- coding: utf8
#
import os
import re
import time
import json
import hashlib
import httplib
import urllib
import random
import logging
import string
from wx_consts import *
from wx_messages import *
from wx_events import *

logging.basicConfig(level=logging.DEBUG, format='(%(funcName)-10s) %(message)s')
# 设置关键的认证接口网址
# 设置默认关注回复消息
local_defaults = {
    'def_unsub_flwer': 1,
    #   when user unsubscribe, whos follower should change to?0:no change/1:company/2~:sepcial user
    'def_auth_url': 'http://www.xinzhouzhuan.com/gzh_auther',
    'def_welcome_msg': u'欢迎光临',
}

sys_auth_redirecturi = urllib.quote(local_defaults['def_auth_url'], safe='')
sys_tokens = {}

WORKDIR = ''
QRDIR = ''
HTMLDIR = ''
IMGDIR = ''

def set_page_url(menu, appid='', snsapi_mode='snsapi_userinfo', state=''):
    appid = appid or sys_tokens['tokenid']
    state = state or 'wxgzh'
    def seturl(fromurl):
        if fromurl.startswith('https://open.weixin.qq.com'):
            return fromurl
        url = urllib.quote(fromurl, safe='')
        return 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={snsapi_mode}&state={STATE}#wechat_redirect'.format(APPID=appid,REDIRECT_URI=url,snsapi_mode=snsapi_mode,STATE=state)
    def search_menu(bts):
        for m in bts:
            if isinstance(m, dict):
                if 'url' in m:
                    m['url'] = seturl(m['url'])
                elif 'sub_button' in m:
                    search_menu(m['sub_button'])
    if isinstance(menu, str):
        return seturl(menu)
    elif 'button' in menu:
        search_menu(menu['button'])
    return menu

def escape(s, dquote=None):
    '''Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.'''
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if dquote:
        s = s.replace('"', "&quot;")
    return s

def unescap(s, dquote=None):
    s = s.replace("&amp;", "&") # Must be done first!
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    if dquote:
        s = s.replace('&quot;', '"')
    return s

#   ////////////////////////////////       PART OF MESSAGE GETTER         //////////////////////////////////    
#   ////////////////////////////////       PART OF MESSAGE GETTER         //////////////////////////////////
#   
#   CLASS that handling get/post request to WX API SERVER
class wx_smsg(object):
    """
    with wx_smsg('get_token', ('grant_type', 'appid', 'secret')) as get_token:
        rt = get_token.get()
    with wx_smsg('get_token', grant_type='', appid='', secret='') as get_token:
    """
    baseurl = 'sz.api.weixin.qq.com'
    post_header = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    get_header = {'Content-Type':'text/html; charset=utf-8'}
    error_rtp = ('errcode', 'errmsg')
    server_mode = 'https'

    def __init__(self, mapname, values=None, baseurl='', postdata=None, post_struct_name='', **kwvalues):
        global sys_tokens
        #   post about: postdata/post_struct_name => for self.post_maker
        if mapname not in wxsmsg_mappings:
            raise KeyError('wxsmsg mapping name [%s] is not exists!' % mapname)
        path,self.keys,self.srtp = wxsmsg_mappings[mapname]
        #   self.srtp: server return pattern
        self.baseurl = baseurl or self.__class__.baseurl
        self.path = ''
        if path:
            if not path.startswith('/'):
                self.path += '/' + path
            else:
                self.path += path
        if 'access_token' in self.keys and not kwvalues.get('access_token'):
            kwvalues['access_token'] = sys_tokens['access_token']
        self.values = values or [kwvalues.get(k, '') for k in self.keys]
        if mapname.startswith('post') and post_struct_name:
            #   if post: more data of post_param_keys
            self.postdata = self.post_maker(post_struct_name, **postdata)
        elif postdata:
            self.postdata = postdata
        
    def post_maker(self, pname, strict=False, **kwargs):
        #   make post data struct from keys in wxsmsg_post_struct
        def _deepsetdict(indict, key, value, strict=strict):
            #   search idct for key,value
            if key in indict:
                if strict:
                    if key in wx_CONSTS and indict[key] not in wx_CONSTS[key]:
                        raise ValueError
                indict[key] = value
                return key,value
            else:
                for _ in indict.itervalues():
                    if isinstance(_, dict):
                        return _deepsetdict(_, key, value)
        if 'pname' in kwargs:
            #   we can set some special pname in wxsmsg_post_struct for quick using
            pname = kwargs.pop('pname')
        pstruct = deepcopy(wxsmsg_post_struct[pname])
        for k,v in kwargs.iteritems():
            _deepsetdict(pstruct, k, v)
        return pstruct

    def __paramstr(self):
        paramstr = ''
        for i in xrange(len(self.keys)):
            v = self.values[i]
            v = v.encode('utf8') if isinstance(v, unicode) else str(v).decode('gbk').encode('utf8')
            paramstr += '='.join((self.keys[i], v)) + '&'
        paramstr = paramstr[:-1]
        return paramstr

    @property
    def server(self):
        return self.baseurl

    @property
    def path_param_url(self):
        #   export url for httplib get
        #   /?+paramstring in utf8
        urlstr = '?'.join((self.path, self.__paramstr()))
        return urlstr

    @property
    def post_params(self):
        #   return list for *args for http request(post): ('POST', 'path', 'parambody', header) => con.reqeust(*post_params)
        urlstr = '?'.join((self.path, self.__paramstr()))
        # pd = urllib.urlencode(self.postdata)
        pd = json.dumps(self.postdata, ensure_ascii=False)
        pr =  'POST',urlstr,pd,self.__class__.post_header
        print pr
        return pr

    def __rt_solve(self, rtstring, mode='JSON'):
        #   check if error!
        if mode != 'JSON':
            return restring
        rt = json.loads(rtstring)
        if 'errcode' in rt and int(rt['errcode']) != 0:
            logging.warning('A Err return From Server!')
        return rt

    def __enter__(self):
        print 'enter with con by baseurl: %s' % self.baseurl
        if self.__class__.server_mode == 'https':
            self.con = httplib.HTTPSConnection(self.baseurl, timeout=5)
        else:
            self.con = httplib.HTTPConnection(self.baseurl, timeout=5)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def _url_file_save(self, url, fp, o=True):
        try:
            uo = urllib.URLopener()
            ufo = uo.open(url)
            data = ufo.read()
            ufo.close()
            fo = open(fp, 'w+b')
            fo.write(data)
            fo.close()
        except:
            logging.warning('not able to save data to file.')
            return None
        return fp

    def get(self, filep=''):
        if self.con:
            purl = self.path_param_url
            print 'get data from: %s' % purl
            self.con.request('GET', purl)
            resp = self.con.getresponse()
            if resp.status == 200:
                if filep:
                    fo = None
                    try:
                        fo = open(filep, 'w+b')
                        fo.write(resp.read())
                    except:
                        self._url_file_save(purl, filep)
                    finally:
                        if fo:
                            fo.close()
                    print 'file save done'
                    return filep
                else:
                    #   perhaps get a file some...
                    rt = resp.read()
                    if isinstance(self.srtp, tuple):
                        print 'response from server: ' + rt
                        return self.__rt_solve(rt)
                    else:
                        return rt
        else:
            raise RuntimeError('NO connection!')

    def post(self):
        if self.con:
            self.con.request(*self.post_params)
            resp = self.con.getresponse()
            jrt = self.__rt_solve(resp.read())
            if 'errcode' in jrt and int(jrt['errcode']) != 0:
                logging.warning(jrt['errmsg'])
                return None
            else:
                return jrt
        else:
            raise RuntimeError('NO connection!')

#   ////////////////////////////////       PART OF GZH_SERVER         //////////////////////////////////    
#   ////////////////////////////////       PART OF GZH_SERVER         //////////////////////////////////
# SERVER HOLDING THE TOKENS
class extserver(object):
    tokentime = 3400
    expire_in = 0
    token = {
        'tokenid': '',
        'tokense': ''
    }
    tokenfile = 'token.py'

    @classmethod
    def get_tokenfile(cls):
        workdir = WORKDIR or os.getcwd()
        filep = os.path.join(workdir, cls.tokenfile)
        if os.path.exists(filep):
            return filep
        else:
            try:
                os.makedirs(workdir)
            except:
                pass
            ff = open(filep, 'w')
            ff.close()
            return filep

    @classmethod
    def set_token(cls, vname, value):
        if hasattr(cls, vname):
            cls.vname = value
        elif vname in cls.token:
            cls.token[vname] = value

    @classmethod
    def token_store(cls):
        filep = cls.get_tokenfile()
        with open(filep, 'w') as ff:
            for k,v in cls.token.items():
                if isinstance(v, int) or v.isdigit():
                    line = k + '=' + str(v) + '\n'
                else:
                    line = k + '="' + str(v) + '"\n'
                ff.write(line)
        return True

    @classmethod
    def load_token(cls):
        filep = cls.get_tokenfile()
        if os.path.exists(filep):
            contx = {}
            ff = open(filep, 'r')
            try:
                exec(ff.read(), globals(), contx)
            except:
                ff.close()
                logging.warning('not able to get token data from file!')
                return None
            # with open(filep, 'r') as ff:
            #   for line in ff:
            #       exec(line.strip('\n'), globals(), contx)
            return contx
        else:
            logging.warning('not able to get token data from file!')
            return None


class gzh(extserver):
    token = {
        #   tokenid: appid; tokense: secret
        'tokenid': '',
        'tokense': '',
        'expires_at': 0,
        'Token': 'alexsum',
        'access_token': '',
        'jsapi_ticket': ''
    }
    page_wxcstrs = {
        # 'url1': wxcstr_url1
    }
    tokenfile = 'wxgzh_token.py'
    checktime = 0
    last_ini_server = 0

    @classmethod
    def ini_token(cls, appid, secret):
        global sys_tokens
        cls.token['tokenid'] = appid
        cls.token['tokense'] = secret
        tokendata = cls.load_token()
        if tokendata and tokendata['tokenid'] == appid and tokendata['tokense'] == secret:
            cls.token.update(tokendata)
            checktime = cls.token['expires_at'] - 300
            if checktime > int(time.time()):
                sys_tokens.update(cls.token)
                cls.checktime = checktime
                return
        cls.update_token(appid, secret)

    @classmethod
    def ini_server(cls, appid, secret, server_menu=None):
        global sys_tokens
        cls.ini_token(appid, secret)
        logging.info(str(sys_tokens))
        if server_menu:
            real_menu = deepcopy(server_menu)
            set_page_url(real_menu)
        with wx_smsg('post_create_menu', access_token=sys_tokens['access_token'], postdata=real_menu) as poster:
            jrt = poster.post()
            if jrt.get('errmsg') == 'ok':
                logging.info('create menu ok!')
            else:
                logging.error('NOT ABLE TO CREATE MENU!')

    @classmethod
    def update_menu(cls, menu_data):
        pass

    @classmethod
    def update_token(cls, appid='', secret=''):
        global sys_tokens
        appid = appid or sys_tokens['tokenid']
        secret = secret or sys_tokens['tokense']
        with wx_smsg('get_token', grant_type='client_credential', appid=appid, secret=secret) as getter:
            jrt = getter.get()
        if 'access_token' in jrt:
            cls.token['tokenid'] = appid
            cls.token['tokense'] = secret
            cls.token['access_token'] = jrt['access_token']
            cls.token['expires_at'] = int(jrt['expires_in']) + int(time.time())
            with wx_smsg('get_jticket', access_token=jrt['access_token'], type='jsapi') as jsapi_getter:
                jtrt = jsapi_getter.get()
            if int(jtrt['errcode']) == 0:
                cls.token['jsapi_ticket'] = jtrt['ticket']
            cls.token_store()
        else:
            raise RuntimeError
        cls.checktime = cls.token['expires_at'] - 300
        sys_tokens.update(cls.token)

    @classmethod
    def __create_sign(cls, url):
        signer = dict.fromkeys(('jsapi_ticket', 'noncestr', 'timestamp', 'url'))
        signer['jsapi_ticket'] =  cls.token['jsapi_ticket']
        signer['noncestr'] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
        signer['timestamp'] = int(time.time())
        signer['url'] = url
        ss = '&'.join(['%s=%s' % (key, signer[key]) for key in sorted(signer)])
        signer['signature'] = hashlib.sha1(ss).hexdigest()
        logging.info(str(signer))
        return signer

    @classmethod
    def make_wxconfig(cls, url, debug=False, applist=None):
        #   export the wx.config({debug,appId,timestamp,nonceStr,signatrue,jsApiList[]}) string
        url = url.split('#')[0]
        if time.time() > cls.checktime:
            cls.update_token()
            #   time is over, since jticket changed, config data from jticket have to update too
            cls.page_wxcstrs.clear()
        if url not in cls.page_wxcstrs:
            logging.info('get signature for url: %s' % url)
            signer = cls.__create_sign(url)
            signer.pop('jsapi_ticket')
            signer.pop('url')
            signer['nonceStr'] = signer.pop('noncestr')
            signer['jsApiList'] = applist or ['checkJsApi', 'onMenuShareTimeline', 'onMenuShareAppMessage', 'chooseImage','uploadImage', 'openLocation', 'getLocation','scanQRCode']
            signer['appId'] = cls.token['tokenid']
            #   MARK: if set debug here should: signer['debug'] = True
            wxcstr = 'wx.config({})'.format(json.dumps(signer))
            #   or wxcstr.replace('"true"', 'true')
            if debug:
                debug_str = ',"debug":true});\n'
            else:
                debug_str = ',"debug":false});\n'
            cls.page_wxcstrs[url] = wxcstr[:-2] + debug_str
        else:
            logging.info('wxconfig for %s is exists and not expire!' % url)
        return cls.page_wxcstrs[url]

    @property
    def jsapi_ticket(self):
        return self.__class__.token['jsapi_ticket']

    @property
    def appid(self):
        return self.__class__.token['tokenid']

    @property
    def secret(self):
        return self.__class__.token['tokense']

    def __check_token_time(self):
        if time.time() > self.__class__.checktime:
            self.__class__.update_token()

    def __init__(self, appid, secret, server_menu=None):
        global sys_tokens
        self.__class__.ini_token(appid, secret)
        logging.info(str(sys_tokens))
        server_menu = server_menu or svr_menu
        print server_menu
        set_page_url(server_menu)
        print server_menu
        with wx_smsg('post_create_menu', access_token=sys_tokens['access_token'], postdata=server_menu) as poster:
            jrt = poster.post()
            if jrt.get('errmsg') == 'ok':
                logging.info('create menu ok!')
            else:
                logging.error('NOT ABLE TO CREATE MENU!')

    def when_geted(self, getdata, fromid=''):
        self.__check_token_time()
        #   anylsis the data from wx server: xml
        if self.get_args.get('signature'):
            print 'test_signature!'
            return self.test_signature(self.get_args, msg_common['test_token'])
        else:
            return ''

    def when_posted(self, pdata, fromid=''):
        self.__check_token_time()
        #   regular get MsgType
        #   pdata: request
        try:
            pdata = pdata.decode('utf8')
        except UnicodeEncodeError:
            pass
        mtype = re.search(r'\<MsgType\>\<\!\[CDATA\[(\w+)\]', pdata, re.M).group(1)
        logging.info('new income with mtype: %s' % mtype)
        if mtype == 'event':
            etype = re.search(r'\<Event\>\<\!\[CDATA\[(\w+)\]', pdata, re.M).group(1)
            rmode = 'event'
            try:
                msger = wxevent_mappings[etype](pdata)
            except KeyError:
                msger = None
            #   do the reg events
            # if self.msger and etype in wxevent_reg_funcs:
            #   for ev in wxevent_reg_funcs[etype]:
            #       ev(self.msger)
        elif mtype in wxsmsg_mappings:
            msger = wxsmsg_mappings[mtype](pdata)
            rmode = 'text' if mtype == 'text' else 'msg'
        else:
            msger = None
        return rmode,msger

    def test_signature(self, formdata, token):
        signature = formdata.get('signature','')
        timestamp = formdata.get('timestamp','')
        nonce = formdata.get('nonce','')
        echostr = formdata.get('echostr','')
        s = [timestamp,nonce,token]
        s.sort()
        s = ''.join(s)
        if (hashlib.sha1(s).hexdigest() == signature):
            print 'testing sinagrure with echostr: %s' % echostr
            return echostr
        else:
            return ''

    def showmsg(self, msger):
        if msger:
            if hasattr(msger, 'showmsg'):
                msg = msger.showmsg()
            else:
                msg = 'no message'
            return '[mode\tmtype\tetype\t]\n[%s\t%s\t%s\t]\n%s' % (self.mode, self.mtype, self.etype, msg)
        else:
            return 'unkown'

    def rt_text(self, touser, content=''):
        #   return text: fromuser is me, touser is openid
        msger = wx_msg_text()
        content = content or (msg_common['def_success'] if self.mtype == 'event' else msg_common['default_text_reply'])
        return msger.make_msg(content=content, ToUserName=touser)

    def msger_action(self, actname, msger, *args, **kwargs):
            if hasattr(msger, actname):
                return getattr(msger, actname)(*args, **kwargs)
            else:
                raise KeyError('Target msger have no action named %s' % actname)