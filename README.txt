Version 0.1

A Very Simple WeiXinGongZhongHao Server.

requirement:
python 2.7
flask 0.10.1 +
use wsgi if needed.

configuration:
wx_conts.py
menu defination, use asci text, do not use u'Unicode' way.

installation:
--

how to use:
python server.py

Files:
wx_consts.py:
all wechat message defined here, and system variables

wx_xmler.py:
basic object for message handler

wx_mssages.py:
implement all wechat messages, collected with: wxrmsg_mappings as hash table
some of messages are implemented.

wx_events.py:
implement all wechat events, collected with: wxevent_mappings as hash table.
some of events are implemented.
make sure there is a wxevent_reg_funcs, all reg function hanle events will be stored in here.
use reg_func to register a function to an event.

wx_gzh.py:
main file, by which we create a wechat public account server, use class gzh

server.py:
http enveronment. use the function:
@app.route('/wxgzh', methods = ['GET', 'POST'])
to handle data switch with wechat server.

wx_runtime_user.py:
testing user class, extend it.